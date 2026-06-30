"""Knowledge QA environment for OPSD validation.

Verifies correctness by extracting \\boxed{} from the response and doing
case-insensitive string comparison against the ground truth answer.
"""

from typing import Union

import ray
import torch

from nemo_rl.environments.math_environment import (
    BaseMathEnvironment,
    MathEnvironmentMetadata,
    _extract_boxed_answer,
)
from nemo_rl.environments.interfaces import EnvironmentReturn
from nemo_rl.environments.utils import chunk_list_to_workers


def _verify_knowledge_answer(response: str, ground_truth: str, mode="loose") -> bool:
    """Check correctness for knowledge QA via case-insensitive string match.

    Extracts \\boxed{} from both the response and the ground truth so the
    comparison works whether the ground truth was stored as a plain entity
    name or as a full assistant response containing \\boxed{...}.
    """
    extracted = _extract_boxed_answer(response)
    if extracted is None:
        print("Theh response format is incorrect.")
        return False
    extracted_gt = _extract_boxed_answer(ground_truth)
    if extracted_gt is None:
        print("The ground truth format is incorrect.")
        extracted_gt = ground_truth
    if extracted.strip().lower() == extracted_gt.strip().lower():
        return True
    if mode == "loose" and extracted_gt.strip().lower() in extracted.strip().lower():
        return True
    return False


@ray.remote
class KnowledgeVerifyWorker:
    def verify(
        self,
        pred_responses: list[str],
        ground_truths: list[str],
        return_extracted_answer: bool = False,
        **kwargs,
    ) -> Union[list[float], tuple[list[float], list[str | None]]]:
        results = []
        extracted_answers: list[str | None] = []
        for response, gt in zip(pred_responses, ground_truths):
            try:
                correct = _verify_knowledge_answer(response, gt)
                results.append(1.0 if correct else 0.0)
                if return_extracted_answer:
                    extracted_answers.append(_extract_boxed_answer(response))
            except Exception:
                results.append(0.0)
                print("The response or ground truth format is incorrect.")
                extracted_answers.append(None)
        if return_extracted_answer:
            return results, extracted_answers
        return results


@ray.remote(max_restarts=-1, max_task_retries=-1)
class KnowledgeEnvironment(BaseMathEnvironment):
    WORKER_CLASS_DICT = {
        "math": KnowledgeVerifyWorker,
    }

    def step(
        self,
        message_log_batch,
        metadata: list[MathEnvironmentMetadata],
        return_extracted_answer: bool = False,
    ) -> EnvironmentReturn[MathEnvironmentMetadata]:
        assistant_response_batch = []
        for conversation in message_log_batch:
            assistant_responses = [
                str(interaction["content"])
                for interaction in conversation
                if interaction["role"] == "assistant"
            ]
            assistant_response_batch.append("".join(assistant_responses))

        ground_truths = [g["ground_truth"] for g in metadata]

        chunked_assistant_response_batch = chunk_list_to_workers(
            assistant_response_batch, self.num_workers
        )
        chunked_ground_truths = chunk_list_to_workers(ground_truths, self.num_workers)

        futures = [
            self.workers[i].verify.remote(
                chunk, ground_truth_chunk, return_extracted_answer,
            )
            for i, (chunk, ground_truth_chunk) in enumerate(
                zip(chunked_assistant_response_batch, chunked_ground_truths)
            )
        ]

        worker_results = ray.get(futures)

        results = []
        extracted_answers: list[str | None] | None = (
            [] if return_extracted_answer else None
        )
        for worker_result in worker_results:
            worker_scores = worker_result
            if return_extracted_answer:
                worker_scores, worker_answers = worker_result
                extracted_answers.extend(worker_answers)
            results.extend(worker_scores)

        observations = [
            {
                "role": "environment",
                "content": "Environment: correct" if result else "Environment: incorrect",
            }
            for result in results
        ]

        rewards = torch.tensor(results).cpu()
        done = torch.ones_like(rewards).cpu()
        next_stop_strings = [None] * len(message_log_batch)

        return EnvironmentReturn(
            observations=observations,
            metadata=metadata,
            next_stop_strings=next_stop_strings,
            rewards=rewards,
            terminateds=done,
            answers=extracted_answers,
        )

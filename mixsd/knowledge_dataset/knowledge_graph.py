import random
from typing import List, Dict, Optional
from mixsd.knowledge_dataset.metadata import (
    DOMAINS, RELATION_SCHEMA, ENTITIES, RELATION_TEMPLATES
)


class KnowledgeGraphBuilder:
    """
    Builds knowledge graph structures for single-step and multi-step reasoning tasks.

    The builder creates 14 balanced dictionaries (one per domain) using a coin-flip
    strategy to assign cross-domain edges, ensuring no duplication and approximately
    balanced distribution.
    """

    def __init__(
        self,
        seed: int = 42,
        num_domains: Optional[int] = None,
        num_entities: Optional[int] = None,
    ):
        """
        Initialize the knowledge graph builder.

        Args:
            seed: Random seed for reproducibility
            num_domains: If set, use only the first N domains from DOMAINS
            num_entities: If set, use only the first M entities per domain
        """
        if num_domains is not None:
            self.domains = list(DOMAINS[:num_domains])
        else:
            self.domains = list(DOMAINS)

        selected = set(self.domains)

        if num_entities is not None:
            self.entities = {d: list(ENTITIES[d][:num_entities]) for d in self.domains}
        else:
            self.entities = {d: list(ENTITIES[d]) for d in self.domains}

        self.relation_schema = {
            pair: rels for pair, rels in RELATION_SCHEMA.items()
            if pair[0] in selected and pair[1] in selected
        }
        self.seed = seed

        # Domain to index mapping for consistent ordering
        self.domain_to_idx = {d: i for i, d in enumerate(self.domains)}

        # Precompute outgoing relations by domain
        self.outgoing = {}
        for (src_dom, tgt_dom), rels in self.relation_schema.items():
            self.outgoing.setdefault(src_dom, []).append((tgt_dom, rels))

        # Precompute inverse relation pairs that share a verb in their
        # relative templates (e.g., "disrupts" / "is_disrupted_by" both
        # produce descriptions containing "disrupts").  These can make
        # multi-hop questions non-deterministic.
        self._inverse_pairs, self._verb_object_map = \
            self._find_inverse_relation_pairs()

    def _get_responsible_domain(self, dom1: str, dom2: str) -> str:
        """
        Determine which domain is responsible for storing edges between dom1 and dom2.

        Uses deterministic hash-based coin flip for consistent assignment.

        Args:
            dom1: First domain
            dom2: Second domain

        Returns:
            The domain responsible for storing edges between dom1 and dom2
        """
        # Create canonical ordered pair for consistent hashing
        sorted_pair = tuple(sorted([dom1, dom2]))
        # Deterministic assignment using hash with seed
        h = hash((sorted_pair, self.seed)) % 2
        return sorted_pair[h]

    def _find_inverse_relation_pairs(self):
        """
        Find semantically inverse relation pairs whose relative templates
        share a verb, creating potential ambiguity.

        For example, "disrupts" has template "what {e1} disrupts" and
        "is_disrupted_by" has "what disrupts {e1}".  If both edges exist
        for the same entity, "the X that disrupts A" is non-deterministic.

        Returns:
            (inverse_pairs, verb_object_map) where:
            - inverse_pairs: list of (fwd_rel, inv_rel, verb) tuples
            - verb_object_map: dict mapping relation -> (verb, object_role)
              where object_role is 'entity1' or 'entity2' indicating which
              entity is the "object" of the shared verb.
        """
        # Collect forward-phrased templates: "what {e1} [verb]"
        fwd_verbs = {}  # verb -> [relation_key]
        # Collect reverse-phrased templates: "what [verb] {e1}"
        rev_verbs = {}  # verb -> [relation_key]

        for rel_key, tmpl in RELATION_TEMPLATES.items():
            if isinstance(rel_key, tuple):
                continue
            if not isinstance(tmpl, dict) or 'relative' not in tmpl:
                continue
            relative = tmpl['relative']

            if relative.startswith('what {e1} '):
                verb = relative[10:].strip()
                fwd_verbs.setdefault(verb, []).append(rel_key)
            elif relative.startswith('what ') and '{e1}' in relative:
                before_e1 = relative.split('{e1}')[0][5:].strip()
                rev_verbs.setdefault(before_e1, []).append(rel_key)

        # Find verbs that appear in both forward and reverse forms
        inverse_pairs = []
        for verb in set(fwd_verbs) & set(rev_verbs):
            for fwd_rel in fwd_verbs[verb]:
                for inv_rel in rev_verbs[verb]:
                    inverse_pairs.append((fwd_rel, inv_rel, verb))

        # Build a lookup: for each relation in an inverse pair, which entity
        # is the "object" of the shared verb?
        #   Forward  "disrupts":       (A, disrupts, B)       → B is disrupted → object = entity2
        #   Inverse  "is_disrupted_by": (A, is_disrupted_by, B) → A is disrupted → object = entity1
        verb_object_map = {}
        for fwd_rel, inv_rel, verb in inverse_pairs:
            verb_object_map[fwd_rel] = (verb, 'entity2')
            verb_object_map[inv_rel] = (verb, 'entity1')

        return inverse_pairs, verb_object_map

    def generate_single_step_dictionaries(self) -> List[List[Dict]]:
        """
        Generate 14 knowledge dictionaries, one per domain.

        Assignment rules:
        - Cross-domain edges: coin flip assigns to one of the two domains

        All entities from metadata.py are included (exhaustive coverage).
        Relations are sampled correspondingly for variety.

        Uniqueness constraints (to avoid ambiguous QA):
        - Each (entity1, relation) pair maps to exactly one entity2
        - Each (relation, entity2) pair maps to exactly one entity1
        - Semantic verb uniqueness: for inverse relation pairs (e.g.,
          "disrupts" / "is_disrupted_by"), the same entity cannot be the
          "object" of the shared verb from two different edges.  This
          prevents questions like "what disrupts X?" from having two
          valid answers.

        Returns:
            List of 14 lists, where each inner list contains dicts of format:
            {"entity1": str, "relation": str, "entity2": str}
        """
        rng = random.Random(self.seed)
        domain_dicts = {d: [] for d in self.domains}

        # Track used pairs to ensure uniqueness:
        # - used_outgoing: (entity1, relation) -> True (no duplicate outgoing relations)
        # - used_incoming: (relation, entity2) -> True (no duplicate incoming relations)
        used_outgoing = set()
        used_incoming = set()

        # Track semantic verb usage to prevent ambiguity from inverse
        # relation pairs.  Key: (entity, verb), where entity is the
        # "object" of the verb (the entity being acted upon).
        # Example: adding (A, is_disrupted_by, B) records (A, "disrupts")
        #          adding (C, disrupts, D)         records (D, "disrupts")
        # If (A, "disrupts") already exists, we skip (C, disrupts, A).
        used_verb_object = set()

        # Collect all domain pairs and shuffle for fair distribution
        domain_pairs = list(self.relation_schema.keys())
        rng.shuffle(domain_pairs)

        # Process each relation type in the schema
        for (src_dom, tgt_dom) in domain_pairs:
            relations = self.relation_schema[(src_dom, tgt_dom)]
            responsible_dom = self._get_responsible_domain(src_dom, tgt_dom)

            src_entities = list(self.entities[src_dom])
            tgt_entities = list(self.entities[tgt_dom])
            rng.shuffle(src_entities)

            # Generate edges for all source entities (exhaustive coverage)
            for src_entity in src_entities:
                # Shuffle relations to try different ones
                shuffled_relations = list(relations)
                rng.shuffle(shuffled_relations)

                for rel in shuffled_relations:
                    # Skip if this (entity1, relation) is already used
                    if (src_entity, rel) in used_outgoing:
                        continue

                    # Find available targets (not already used with this relation)
                    available_targets = [
                        e for e in tgt_entities
                        if (rel, e) not in used_incoming
                    ]

                    if not available_targets:
                        continue

                    # Check semantic verb constraint for inverse relation pairs
                    if rel in self._verb_object_map:
                        verb, object_role = self._verb_object_map[rel]
                        if object_role == 'entity1':
                            # Inverse rel (e.g., is_disrupted_by): entity1 is the object
                            if (src_entity, verb) in used_verb_object:
                                continue
                        # For entity2 role, we filter available_targets below
                        available_targets = [
                            e for e in available_targets
                            if object_role != 'entity2'
                            or (e, verb) not in used_verb_object
                        ]
                        if not available_targets:
                            continue

                    # Sample target entity
                    tgt_entity = rng.choice(available_targets)

                    # Mark as used
                    used_outgoing.add((src_entity, rel))
                    used_incoming.add((rel, tgt_entity))

                    # Mark semantic verb usage
                    if rel in self._verb_object_map:
                        verb, object_role = self._verb_object_map[rel]
                        obj_entity = src_entity if object_role == 'entity1' else tgt_entity
                        used_verb_object.add((obj_entity, verb))

                    edge = {
                        "entity1": src_entity,
                        "relation": rel,
                        "entity2": tgt_entity
                    }
                    domain_dicts[responsible_dom].append(edge)
                    break

        # Return as list ordered by DOMAINS
        return [domain_dicts[d] for d in self.domains]

    def generate_flat_knowledge_base(self) -> List[Dict]:
        """
        Generate a flat knowledge base (all edges combined).

        This is useful for multi-step reasoning where we need to traverse
        across all domains.

        Returns:
            List of edge dicts: {"entity1": str, "relation": str, "entity2": str}
        """
        domain_dicts = self.generate_single_step_dictionaries()
        flat_kb = []
        for domain_edges in domain_dicts:
            flat_kb.extend(domain_edges)
        return flat_kb

    def generate_question_answer_pairs(
        self,
        knowledge_dicts: Optional[List[List[Dict]]] = None,
        question_type: str = "both"
    ) -> List[List[Dict]]:
        """
        Generate question-answer pairs from knowledge dictionaries.

        Args:
            knowledge_dicts: The 14 domain dictionaries (if None, generates new ones)
            question_type: "relation" (ask about relation as MCQ), "entity" (ask about entity2),
                          or "both" (both types)

        Returns:
            List of 14 lists, where each inner list contains dicts:
            - For "entity" type: {"question": str, "answer": str, "type": str}
            - For "relation" type (MCQ): {
                "question": str,
                "options": {"A": str, "B": str, "C": str, "D": str},
                "answer": str (A/B/C/D),
                "type": str
              }
        """
        if knowledge_dicts is None:
            knowledge_dicts = self.generate_single_step_dictionaries()

        rng = random.Random(self.seed)
        qa_pairs = []

        for domain_edges in knowledge_dicts:
            domain_qa = []

            for edge in domain_edges:
                entity1 = edge["entity1"]
                relation = edge["relation"]
                entity2 = edge["entity2"]

                # Get template for this relation (with fallback)
                template = RELATION_TEMPLATES.get(relation)

                if question_type in ("relation", "both"):
                    # Generate MCQ for relation question
                    mcq = self._generate_relation_mcq(
                        entity1, relation, entity2, template, rng
                    )
                    domain_qa.append(mcq)

                if question_type in ("entity", "both"):
                    # Question asking about entity2 using template
                    # Look up template by (relation, target_domain) first, then fall back to relation only
                    tgt_domain = self._find_entity_domain(entity2)
                    template_key = (relation, tgt_domain)
                    template = RELATION_TEMPLATES.get(template_key) or RELATION_TEMPLATES.get(relation)

                    if template:
                        q_entity = template["question"].format(e1=entity1, e2=entity2)
                    else:
                        rel_formatted = relation.replace('_', ' ')
                        domain_label = self._domain_to_label(tgt_domain) if tgt_domain else "entity"
                        q_entity = f"Which {domain_label} {rel_formatted} {entity1}?"

                    # Inject domain hint for unambiguous answer type
                    if tgt_domain:
                        q_entity = self._add_domain_hint_to_question(q_entity, tgt_domain)

                    domain_qa.append({
                        "question": q_entity,
                        "answer": entity2,
                        "type": "entity"
                    })

            qa_pairs.append(domain_qa)

        return qa_pairs

    def _generate_relation_mcq(
        self,
        entity1: str,
        correct_relation: str,
        entity2: str,
        correct_template: Optional[Dict],
        rng: random.Random
    ) -> Dict:
        """
        Generate a multiple choice question for relation identification.

        Returns a dict with:
        - question: The MCQ question
        - options: {"A": stmt, "B": stmt, "C": stmt, "D": stmt}
        - answer: The correct option letter (A/B/C/D)
        - type: "relation"
        """
        # Find the domain pair for this edge
        src_domain = self._find_entity_domain(entity1)
        tgt_domain = self._find_entity_domain(entity2)

        # Get all relations for this domain pair
        domain_pair = (src_domain, tgt_domain)
        available_relations = self.relation_schema.get(domain_pair, [])

        # Generate the correct statement
        if correct_template:
            correct_statement = correct_template["statement"].format(
                e1=entity1, e2=entity2
            )
        else:
            rel_formatted = correct_relation.replace('_', ' ')
            correct_statement = f"{entity1} {rel_formatted} {entity2}."

        # Sample 3 distractor relations (different from the correct one)
        distractor_relations = [r for r in available_relations if r != correct_relation]
        if len(distractor_relations) >= 3:
            distractor_relations = rng.sample(distractor_relations, 3)
        else:
            # If not enough relations in this pair, pad with variations
            while len(distractor_relations) < 3:
                # Create a placeholder distractor
                distractor_relations.append(None)

        # Generate distractor statements
        distractor_statements = []
        for dist_rel in distractor_relations:
            if dist_rel is None:
                # Fallback: slightly modify the correct statement
                distractor_statements.append(f"{entity1} is related to {entity2}.")
            else:
                dist_template = RELATION_TEMPLATES.get(dist_rel)
                if dist_template:
                    stmt = dist_template["statement"].format(e1=entity1, e2=entity2)
                else:
                    rel_formatted = dist_rel.replace('_', ' ')
                    stmt = f"{entity1} {rel_formatted} {entity2}."
                distractor_statements.append(stmt)

        # Combine and shuffle options
        all_options = [correct_statement] + distractor_statements
        rng.shuffle(all_options)

        # Find which position has the correct answer
        correct_index = all_options.index(correct_statement)
        option_letters = ["A", "B", "C", "D"]
        correct_letter = option_letters[correct_index]

        # Build the options dict
        options = {
            letter: stmt for letter, stmt in zip(option_letters, all_options)
        }

        # Build question string with options included
        question_with_options = f"What is the relationship between {entity1} and {entity2}?\n"
        question_with_options += "\n".join(
            f"{letter}) {stmt}" for letter, stmt in options.items()
        )

        return {
            "question": question_with_options,
            "options": options,
            "answer": correct_letter,
            "type": "relation"
        }

    def _extract_relation_phrase(self, statement_template: str) -> str:
        """Extract the relation phrase from a statement template."""
        # Template format: "{e1} [relation phrase] {e2}."
        template = statement_template.rstrip('.')
        # Remove the entity placeholders to get the relation
        parts = template.split('{e1}')
        if len(parts) > 1:
            relation_part = parts[1].split('{e2}')[0].strip()
            return relation_part
        return template

    def generate_statements(
        self,
        knowledge_dicts: Optional[List[List[Dict]]] = None
    ) -> List[List[str]]:
        """
        Generate natural language statements from knowledge dictionaries.

        Args:
            knowledge_dicts: The 14 domain dictionaries (if None, generates new ones)

        Returns:
            List of 14 lists, where each inner list contains statement strings
        """
        if knowledge_dicts is None:
            knowledge_dicts = self.generate_single_step_dictionaries()

        statements = []

        for domain_edges in knowledge_dicts:
            domain_statements = []

            for edge in domain_edges:
                entity1 = edge["entity1"]
                relation = edge["relation"]
                entity2 = edge["entity2"]

                # Get template for this relation
                template = RELATION_TEMPLATES.get(relation)

                if template:
                    # Use template for natural language statement
                    statement = template["statement"].format(e1=entity1, e2=entity2)
                else:
                    # Fallback to simple format
                    rel_formatted = relation.replace('_', ' ')
                    statement = f"{entity1} {rel_formatted} {entity2}."

                domain_statements.append(statement)

            statements.append(domain_statements)

        return statements

    def _find_entity_domain(self, entity: str) -> Optional[str]:
        """Find which domain an entity belongs to."""
        for domain, entities in self.entities.items():
            if entity in entities:
                return domain
        return None

    def _domain_to_label(self, domain: str) -> str:
        """Convert domain name to a readable lowercase label for use in questions."""
        labels = {
            'Person': 'person',
            'Location': 'location',
            'Organization': 'organization',
            'Event': 'event',
            'Profession': 'profession',
            'Hobby': 'hobby',
            'Skill': 'skill',
            'PhysicalObject': 'object',
            'Product': 'product',
            'Service': 'service',
            'MediaWork': 'media work',
            'DigitalTool': 'digital tool',
            'Task': 'task',
            'TimePeriod': 'time period',
        }
        return labels.get(domain, domain.lower())

    def _add_domain_hint_to_question(self, question: str, tgt_domain: str) -> str:
        """
        Inject the target domain into a question so the answer type is unambiguous.

        Examples:
            "What does {e1} support?"          + Task       -> "What task does {e1} support?"
            "What inspires {e1}?"              + Hobby      -> "What hobby inspires {e1}?"
            "What is {e1} compatible with?"    + Product    -> "What product is {e1} compatible with?"
            "What organization does {e1} ..."  + Org        -> unchanged (already has hint)
            "Where was {e1} born?"             + Location   -> unchanged (already domain-specific)
            "Who does {e1} mentor?"            + Person     -> unchanged (already domain-specific)
        """
        domain_label = self._domain_to_label(tgt_domain)

        # Only modify questions starting with "What" (generic)
        # Skip if already has a domain hint right after "What"
        if not question.lower().startswith("what "):
            return question

        after_what = question[5:]  # everything after "What "

        # Check if already has a domain hint (e.g., "What organization does ...")
        all_labels = {self._domain_to_label(d) for d in self.domains}
        first_word = after_what.split()[0].lower() if after_what.split() else ""
        # Also check two-word labels like "media work", "digital tool", "time period"
        first_two = " ".join(after_what.split()[:2]).lower() if len(after_what.split()) >= 2 else ""
        if first_word in all_labels or first_two in all_labels:
            return question

        return f"What {domain_label} " + after_what

    def validate_knowledge_base(self, knowledge_base: List[Dict]) -> Dict:
        """
        Validate that a knowledge base has no ambiguous edges.

        Checks:
        1. Forward uniqueness: each (entity1, relation) maps to exactly one entity2
        2. Reverse uniqueness: each (relation, entity2) maps to exactly one entity1
        3. Semantic verb uniqueness: no entity is the "object" of a shared verb
           from two different inverse-pair edges

        Args:
            knowledge_base: Flat list of edge dicts

        Returns:
            Dict with 'valid' (bool) and 'violations' (list of issue strings)
        """
        violations = []

        # Check 1: forward uniqueness
        fwd = {}
        for edge in knowledge_base:
            key = (edge['entity1'], edge['relation'])
            if key in fwd and fwd[key] != edge['entity2']:
                violations.append(
                    f"Forward duplicate: ({key[0]}, {key[1]}) -> "
                    f"{fwd[key]} AND {edge['entity2']}")
            fwd[key] = edge['entity2']

        # Check 2: reverse uniqueness
        rev = {}
        for edge in knowledge_base:
            key = (edge['relation'], edge['entity2'])
            if key in rev and rev[key] != edge['entity1']:
                violations.append(
                    f"Reverse duplicate: ({key[0]}, {key[1]}) -> "
                    f"{rev[key]} AND {edge['entity1']}")
            rev[key] = edge['entity1']

        # Check 3: semantic verb uniqueness
        verb_objects = {}  # (entity, verb) -> edge info
        for edge in knowledge_base:
            rel = edge['relation']
            if rel not in self._verb_object_map:
                continue
            verb, object_role = self._verb_object_map[rel]
            obj_entity = edge['entity1'] if object_role == 'entity1' else edge['entity2']
            key = (obj_entity, verb)
            if key in verb_objects and verb_objects[key] != edge:
                violations.append(
                    f"Semantic verb ambiguity: \"{verb}\" applied to "
                    f"{obj_entity} from edges "
                    f"({verb_objects[key]['entity1']}, {verb_objects[key]['relation']}, "
                    f"{verb_objects[key]['entity2']}) AND "
                    f"({edge['entity1']}, {edge['relation']}, {edge['entity2']})")
            verb_objects[key] = edge

        return {
            'valid': len(violations) == 0,
            'violations': violations,
            'num_edges': len(knowledge_base),
        }

    def generate_multi_step_trajectories(
        self,
        allowed_domains: List[str],
        depth: int,
        num_examples: int,
        knowledge_base: List[Dict],
    ) -> List[Dict]:
        """
        Generate multi-step reasoning trajectories by chaining edges from
        the provided atomic knowledge base.

        IMPORTANT: knowledge_base must be the same set of edges used to
        generate the atomic (single-step) training data.  This ensures
        every fact in a compositional question was seen during atomic
        training.

        Args:
            allowed_domains: List of domains to include in trajectories
            depth: Number of steps (edges) in each trajectory
            num_examples: Number of trajectory examples to generate
            knowledge_base: Flat list of atomic edge dicts — REQUIRED

        Returns:
            List of trajectory dicts, each containing:
            {
                "question": str,  # Multi-hop question
                "answer": str,    # Final answer (last entity)
                "path": List[Dict],  # Sequence of edges
                "intermediate_answers": List[str]  # Intermediate entities
            }
        """

        rng = random.Random(self.seed)
        allowed_domains_set = set(allowed_domains)

        # Build an index from entity -> list of outgoing edges
        entity_to_outgoing = {}
        for edge in knowledge_base:
            e1 = edge["entity1"]
            e1_domain = self._find_entity_domain(e1)
            e2_domain = self._find_entity_domain(edge["entity2"])

            # Only include edges where both domains are allowed
            if e1_domain in allowed_domains_set and e2_domain in allowed_domains_set:
                if e1 not in entity_to_outgoing:
                    entity_to_outgoing[e1] = []
                entity_to_outgoing[e1].append(edge)

        # Find valid starting entities (entities that have outgoing edges)
        starting_entities = list(entity_to_outgoing.keys())

        if not starting_entities:
            return []

        results = []
        max_attempts = num_examples * 100
        attempts = 0
        seen_paths = set()

        while len(results) < num_examples and attempts < max_attempts:
            attempts += 1

            # Sample a trajectory
            trajectory = self._sample_trajectory(
                rng, entity_to_outgoing, starting_entities, depth,
                allowed_domains_set,
            )

            if trajectory is None:
                continue

            # Check for uniqueness (based on relation sequence)
            path_key = tuple((e["relation"], self._find_entity_domain(e["entity1"]),
                            self._find_entity_domain(e["entity2"])) for e in trajectory)
            if path_key in seen_paths:
                continue
            seen_paths.add(path_key)

            # Build the multi-hop question
            question = self._build_multi_hop_question(trajectory)
            answer = trajectory[-1]["entity2"]
            intermediate = [edge["entity2"] for edge in trajectory[:-1]]

            results.append({
                "question": question,
                "answer": answer,
                "path": trajectory,
                "intermediate_answers": intermediate
            })

        return results

    def _sample_trajectory(
        self,
        rng: random.Random,
        entity_to_outgoing: Dict[str, List[Dict]],
        starting_entities: List[str],
        depth: int,
        allowed_domains_set: set,
    ) -> Optional[List[Dict]]:
        """Sample a single acyclic trajectory of given depth."""
        current_entity = rng.choice(starting_entities)
        path = []
        visited_entities = {current_entity}

        for _ in range(depth):
            if current_entity not in entity_to_outgoing:
                return None

            outgoing_edges = entity_to_outgoing[current_entity]

            # Filter: allowed domains + no entity revisit
            valid_edges = [
                e for e in outgoing_edges
                if self._find_entity_domain(e["entity2"]) in allowed_domains_set
                and e["entity2"] not in visited_entities
            ]

            if not valid_edges:
                return None

            edge = rng.choice(valid_edges)
            path.append(edge.copy())

            current_entity = edge["entity2"]
            visited_entities.add(current_entity)

        return path

    def _build_multi_hop_question(self, trajectory: List[Dict]) -> str:
        """
        Build a multi-hop question from a trajectory using natural language templates.

        Uses domain-typed relative clauses (e.g., "the organization that {e1} advises")
        instead of generic "what" references to ensure readability and unambiguous
        entity resolution at every hop.

        Example: "What event does the organization where Yuki Brennan is a board member's
                  competitor announce at?"
        """
        # For single step, use the question template directly
        if len(trajectory) == 1:
            edge = trajectory[0]
            tgt_domain = self._find_entity_domain(edge["entity2"])
            template_key = (edge["relation"], tgt_domain)
            template = RELATION_TEMPLATES.get(template_key) or RELATION_TEMPLATES.get(edge["relation"])
            if template:
                question = template["question"].format(e1=edge["entity1"], e2=edge["entity2"])
            else:
                final_rel = edge["relation"].replace('_', ' ')
                domain_label = self._domain_to_label(tgt_domain) if tgt_domain else "entity"
                question = f"Which {domain_label} {final_rel} {edge['entity1']}?"
            if tgt_domain:
                question = self._add_domain_hint_to_question(question, tgt_domain)
            return question

        # Multi-step: build description using relative clause templates
        # Start with the innermost entity (first entity in trajectory)
        description = trajectory[0]["entity1"]

        # Build up the description by chaining relative clauses
        for edge in trajectory[:-1]:
            relation = edge["relation"]
            tgt_domain = self._find_entity_domain(edge["entity2"])

            # Check for domain-specific template override first
            template_key = (relation, tgt_domain)
            template = RELATION_TEMPLATES.get(template_key) or RELATION_TEMPLATES.get(relation)

            if template:
                relative = template["relative"]
                # Replace generic "what" with domain-typed reference for clarity
                # and unambiguous entity resolution
                if relative.lower().startswith("what "):
                    domain_label = self._domain_to_label(tgt_domain) if tgt_domain else "entity"
                    relative = f"the {domain_label} that " + relative[5:]
                description = relative.format(e1=description, e2=edge["entity2"])
            else:
                # Fallback to generic format with domain type
                rel = relation.replace('_', ' ')
                domain_label = self._domain_to_label(tgt_domain) if tgt_domain else "entity"
                description = f"the {domain_label} that {rel} {description}"

        # Generate the final question using the last edge's question template
        final_edge = trajectory[-1]
        final_relation = final_edge["relation"]
        final_tgt_domain = self._find_entity_domain(final_edge["entity2"])
        template_key = (final_relation, final_tgt_domain)
        final_template = RELATION_TEMPLATES.get(template_key) or RELATION_TEMPLATES.get(final_relation)

        if final_template:
            question = final_template["question"].format(e1=description, e2=final_edge["entity2"])
        else:
            final_rel = final_relation.replace('_', ' ')
            domain_label = self._domain_to_label(final_tgt_domain) if final_tgt_domain else "entity"
            question = f"Which {domain_label} {final_rel} {description}?"

        # Inject domain hint for unambiguous answer type
        if final_tgt_domain:
            question = self._add_domain_hint_to_question(question, final_tgt_domain)

        return question

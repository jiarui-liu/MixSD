"""Shared SFT entry-point helper for the *_opsd dataset directories.

Each dataset's run_sft.py is a thin shim that imports `run` from this module
and passes in its own `register_opsd_datasets` callback. The script must be
launched with cwd inside the dataset directory so the local config and
register_dataset module resolve correctly.
"""

import argparse
import os
import sys


def run(register_datasets):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--config", type=str, required=True)
    args, overrides = parser.parse_known_args()

    from omegaconf import OmegaConf
    from nemo_rl.utils.config import (
        load_config,
        parse_hydra_overrides,
        register_omegaconf_resolvers,
    )

    register_omegaconf_resolvers()
    cfg = load_config(args.config)
    if overrides:
        cfg = parse_hydra_overrides(cfg, overrides)
    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    register_datasets(cfg_dict["paths"]["data_dir"])

    nemo_rl_examples = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "nemo-rl", "examples")
    )
    if nemo_rl_examples not in sys.path:
        sys.path.insert(0, nemo_rl_examples)
    import run_sft as _sft

    _sft.main()

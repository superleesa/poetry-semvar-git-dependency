from poetry.core.constraints.version.parser import parse_single_constraint


def is_sem_ver_constraint(sem_ver: str) -> bool:
    # see: https://github.com/dazza-codes/poetry/blob/92e260311e37ebe5570fc88410ab93c5fc0506ff/poetry/semver/__init__.py#L17-L27
    try:
        parse_single_constraint(sem_ver)
        return True
    except (TypeError, ValueError):
        return False

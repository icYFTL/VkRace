def set_args(e_code: str, fully=True, **kwargs) -> str:  # CAUSE I DON'T HAVE GOOD DOCS
    for key in list(kwargs.keys()):
        if f'Args.{key}' not in e_code:
            raise Exception(f'Key {key} not found in e_code')

        e_code = e_code.replace(f'Args.{key}', str(kwargs[key]))
    if fully and 'Args.' in e_code:
        raise Exception('Not enough args passed')

    return e_code

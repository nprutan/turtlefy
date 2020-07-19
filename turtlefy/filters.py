
def pass_verification_pipeline(funcs_to_apply, resource, options=None):
    for func in funcs_to_apply:
        if not func(resource, options):
            return False
    return True

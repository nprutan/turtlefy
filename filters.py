
def pass_verification_pipeline(funcs_to_apply, resource):
    for func in funcs_to_apply:
        if not func(resource):
            return False
    return True

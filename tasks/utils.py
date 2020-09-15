def run_command(command, context, logger=None, **kwargs):
    if logger:
        logger.debug(f'executing {command}')
    context.run(command, **kwargs)

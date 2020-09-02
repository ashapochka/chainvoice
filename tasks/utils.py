def run_command(command, context, logger=None):
    if logger:
        logger.debug('executing %s', command)
    context.run(command)

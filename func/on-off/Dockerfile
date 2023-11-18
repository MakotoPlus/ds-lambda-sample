FROM public.ecr.aws/lambda/python:3.11

ENV LOGGER_CONFIG "logger.config"
# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}
COPY logger.config ${LAMBDA_TASK_ROOT}/.
# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY * ${LAMBDA_TASK_ROOT}/.
#ENTRYPOINT ["pytest"]
ENTRYPOINT ["pytest", "-svv"]
#ENTRYPOINT ["pytest", "-svv", "pytest/test_ec2_ctrl.py"]
#ENTRYPOINT ["pytest", "-svv", "pytest/test_ec2_ctrl.py"]

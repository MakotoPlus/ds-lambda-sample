FROM public.ecr.aws/lambda/python:3.9

ENV LOG_LEVEL="DEBUG"
ENV PATH_ROOT=${LAMBDA_TASK_ROOT}
# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}
# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY * ${LAMBDA_TASK_ROOT}/.
#ENTRYPOINT ["pytest"]
ENTRYPOINT ["pytest", "-sxvv"]
#ENTRYPOINT ["pytest", "-xsvv", "pytest/service/test_rds_ctrl.py"]


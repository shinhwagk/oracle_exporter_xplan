FROM python:3
RUN pip install xplan
WORKDIR /app
ADD grafana_xplan.py .
CMD python grafana_xplan.py -cf dsns.json
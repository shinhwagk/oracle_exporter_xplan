FROM shinhwagk/oraclepython:latest
RUN python3 -m pip install xplan
WORKDIR /app
ADD grafana_xplan.py .
ENTRYPOINT python3 grafana_xplan.py -cf dsns.json
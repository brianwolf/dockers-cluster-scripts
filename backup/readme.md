# Agregar cron al script

## Comandos

1) Ejecutar

    ```bash
    crontab -e
    ```

2) Agregar lo siguiente

    ```bash
    0 4 * * * python3 /home/brian/Workspace/dockers-cluster-scripts/backup/script.py
    ```

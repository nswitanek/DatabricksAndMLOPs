# Databricks notebook source
# MAGIC %md
# MAGIC # Mounting Blob Storage

# COMMAND ----------

container_name = dbutils.widgets.get("CONTAINER_NAME", "")
account_name = dbutils.widgets.get("ACCOUNT_NAME", "")
secret_name = dbutils.widgets.get("SECRET_NAME", "amlstoragekey")
scope_name = dbutils.widgets.get("SCOPE_NAME", "demoscope")
mount_name = dbutils.widgets.get("MOUNT_NAME", "data")

if mount_name in dbutils.fs.mounts():
    print(f"Mount '{mount_name}' already exists!")
else:
    print(f"Executing mount of '{mount_name}'")
    wasbs_path = f"wasbs://{container_name}@{account_name}.blob.core.windows.net"
    conf_key = f"fs.azure.account.key.{account_name}.blob.core.windows.net"
    secret_value = dbutils.secrets.get(scope = scope_name, key = secret_name)
    dbutils.fs.mount(
        source = wasbs_path,
        mount_point = f"/mnt/{mount_name}",
        extra_configs = {conf_key:secret_value}
    )

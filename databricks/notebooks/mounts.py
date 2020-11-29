dbutils.widgets.text("CONTAINER_NAME", "data")
dbutils.widgets.text("ACCOUNT_NAME", "")
dbutils.widgets.text("SECRET_NAME", "")
dbutils.widgets.text("SCOPE_NAME", "demoscope")
dbutils.widgets.text("MOUNT_NAME", "data")

dbutils.widgets.get("CONTAINER_NAME")
dbutils.widgets.get("ACCOUNT_NAME")
dbutils.widgets.get("SECRET_NAME")
dbutils.widgets.get("SCOPE_NAME")
dbutils.widgets.get("MOUNT_NAME")
container_name =  getArgument("CONTAINER_NAME")
account_name =  getArgument("ACCOUNT_NAME") 
secret_name = getArgument("SECRET_NAME")
scope_name = getArgument("SCOPE_NAME")
mount_name = getArgument("MOUNT_NAME")

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
    display(dbutils.fs.mounts())
import pandas as pd
import gc

def get_id(data: pd.DataFrame) -> pd.DataFrame:
    data["Id"] = data.CodigoDC.astype(str) + data.Cliente.astype(str) + data.Marca.astype(str) + data.Cupo.astype(str)
    data = data.set_index("Id")
    return data

def get_data_frame_target(active_promos: pd.DataFrame, executed_promos: pd.DataFrame) -> pd.DataFrame:
    active_promos = get_id(active_promos)
    executed_promos = get_id(executed_promos)

    executed_promos["target"] = 1
    active_promos = active_promos.join(executed_promos.target).replace(np.nan, 0)
    active_promos = active_promos.reset_index().drop("Id", axis=1)
    return active_promos

def mergue_client_attr_target_df(clients_attr: pd.DataFrame, data_frame_target: pd.DataFrame) -> pd.DataFrame:
    clients_attr = clients_attr.set_index("Cliente")
    data_frame_target = data_frame_target.set_index("Cliente")
    data_frame_target = data_frame_target.join(clients_attr)
    data_frame_target = data_frame_target.reset_index()
    return data_frame_target

def get_sales_df(sales: pd.DataFrame) -> pd.DataFrame:
    sales = sales.dropna()
    to_dummies_sales = ["ClaseEnvase", "SegmentoPrecio"]
    Descuento = pd.get_dummies(sales.Dcto == 0)
    Descuento.columns = ["ConDescuento", "SinDescuento"]
    Nr = pd.get_dummies(sales.Nr < 0)
    Nr.columns = ["NrPositivo", "NrNegativo"]
    ClaseEnvase = pd.get_dummies(sales.ClaseEnvase, prefix = "ClaseEnvase")
    SegmentoPrecio = pd.get_dummies(sales.SegmentoPrecio.astype(int), prefix = "SegmentoPrecio")
    sales = sales.join(Descuento).join(Nr).join(ClaseEnvase).join(SegmentoPrecio)
    sales["MesCod"] = sales.Año.astype(str) + sales.Mes.map("{:02}".format)
    sales["MesCod"] = sales.MesCod.astype(int)
    sales["Cupo"] = sales.Cupo.astype(int)
    return sales.drop(["Año", "Mes"], axis=1).drop(to_dummies_sales, axis=1)

def marca_cupo_sales_df(sales: pd.DataFrame, meses) -> pd.DataFrame:
    sales = get_sales_df(sales)
    df_1 = sales.groupby(["MesCod", "Cliente", "Marca", "Cupo"]).sum().sort_index().astype("int32")
    sales_complementos = []
    for mes in meses.keys():
        res_sum = pd.concat([
            df_1.loc[meses[mes]].groupby(["Cliente", "Marca", "Cupo"]).sum()
        ], axis=1)
        res_sum["MesCod"] = mes
        res_sum = res_sum.reset_index().set_index(["Cliente", "Marca", "Cupo", "MesCod"]).astype("float32").add_suffix('_sum')

        res_min = pd.concat([
            df_1.loc[meses[mes]].groupby(["Cliente", "Marca", "Cupo"]).min()
        ], axis=1)
        res_min["MesCod"] = mes
        res_min = res_min.reset_index().set_index(["Cliente", "Marca", "Cupo", "MesCod"]).astype("float32").add_suffix('_min')

        res_max = pd.concat([
            df_1.loc[meses[mes]].groupby(["Cliente", "Marca", "Cupo"]).max()
        ], axis=1)
        res_max["MesCod"] = mes
        res_max = res_max.reset_index().set_index(["Cliente", "Marca", "Cupo", "MesCod"]).astype("float32").add_suffix('_max')

        res_std = pd.concat([
            df_1.loc[meses[mes]].groupby(["Cliente", "Marca", "Cupo"]).std()
        ], axis=1)
        res_std["MesCod"] = mes
        res_std = res_std.reset_index().set_index(["Cliente", "Marca", "Cupo", "MesCod"]).astype("float32").add_suffix('_std')

        sales_complementos.append(res_sum.join(res_min).join(res_max).join(res_std))

    gc.collect()
    sales_complementos = pd.concat(sales_complementos)
    return sales_complementos

def personal_info_sales_df(sales: pd.DataFrame, meses) -> pd.DataFrame:
    sales = get_sales_df(sales)
    df_1 = sales.drop(["Marca", "Cupo"], axis = 1).groupby(["MesCod", "Cliente"]).sum().sort_index().astype("int32")
    sales_complementos = []
    for mes in meses.keys():
        res_sum = pd.concat([
            df_1.loc[meses[mes]].groupby("Cliente").sum()
        ], axis=1)
        res_sum["MesCod"] = mes
        res_sum = res_sum.reset_index().set_index(["Cliente", "MesCod"]).astype("float32").add_suffix('_cliente_sum')

        res_min = pd.concat([
            df_1.loc[meses[mes]].groupby("Cliente").min()
        ], axis=1)
        res_min["MesCod"] = mes
        res_min = res_min.reset_index().set_index(["Cliente", "MesCod"]).astype("float32").add_suffix('_cliente_min')

        res_max = pd.concat([
            df_1.loc[meses[mes]].groupby("Cliente").max()
        ], axis=1)
        res_max["MesCod"] = mes
        res_max = res_max.reset_index().set_index(["Cliente", "MesCod"]).astype("float32").add_suffix('_cliente_max')

        res_std = pd.concat([
            df_1.loc[meses[mes]].groupby("Cliente").std()
        ], axis=1)
        res_std["MesCod"] = mes
        res_std = res_std.reset_index().set_index(["Cliente", "MesCod"]).astype("float32").add_suffix('_cliente_std')

        sales_complementos.append(res_sum.join(res_min).join(res_max).join(res_std))

    gc.collect()
    print("contatenando complementos")
    sales_complementos = pd.concat(sales_complementos)
    return sales_complementos


def get_train_df(clients_attr: pd.DataFrame, active_promos: pd.DataFrame, executed_promos: pd.DataFrame
                 , marca_cupo_info_sales: pd.DataFrame, personal_info_sales: pd.DataFrame) -> pd.DataFrame:
    data_frame_target = get_data_frame_target(active_promos, executed_promos)
    client_attr_target_df = mergue_client_attr_target_df(clients_attr, data_frame_target)
    client_attr_target_df["MesCod"] = pd.DatetimeIndex(client_attr_target_df.Fecha_Desde).year.astype(str) + pd.DatetimeIndex(
        client_attr_target_df.Fecha_Desde).month.map("{:02}".format).astype(str)
    client_attr_target_df["MesCod"] = client_attr_target_df.MesCod.astype(int)
    client_attr_target_df = client_attr_target_df.set_index(["Cliente", "Marca", "Cupo", "MesCod"]).join(
        marca_cupo_info_sales).reset_index().set_index(["Cliente", "MesCod"]).join(personal_info_sales)
    print("Dataset train terminada.")
    return client_attr_target_df.reset_index()


def get_test_df(test: pd.DataFrame, clients_attr: pd.DataFrame, marca_cupo_info_sales: pd.DataFrame,
                personal_info_sales: pd.DataFrame, MesCod: int) -> pd.DataFrame:
    test["MesCod"] = MesCod
    test = mergue_client_attr_target_df(clients_attr, test)
    test = test.set_index(["Cliente", "Marca", "Cupo", "MesCod"]).join(marca_cupo_info_sales).reset_index().set_index(
        ["Cliente", "MesCod"]).join(personal_info_sales)
    ano = str(MesCod)[0:4]
    mes = str(MesCod)[4:]
    test["Fecha_Hasta"] = pd.to_datetime(str(mes+"/01/"+ano))
    print("Dataset test terminada.")
    return test.reset_index()
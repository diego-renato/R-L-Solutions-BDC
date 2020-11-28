import pandas as pd
import numpy as np


def transform_clients_attr_features(data_final: pd.DataFrame) -> pd.DataFrame:
    to_dummies_clients_attr = ["Region", "Gerencia", "SubCanal", "Estrato", "Mes"]
    data_final["Mes"] = pd.DatetimeIndex(data_final.FechaAltaCliente).month
    data_final["AñosTranscurridos"] = pd.DatetimeIndex(data_final.Fecha_Hasta).year - pd.DatetimeIndex(
        data_final.FechaAltaCliente).year
    data_final["MesesTranscurridos"] = ((pd.DatetimeIndex(data_final.Fecha_Hasta) - pd.DatetimeIndex(
        data_final.FechaAltaCliente)) / np.timedelta64(1, 'D') -
                                        (pd.DatetimeIndex(data_final.Fecha_Hasta).day + pd.DatetimeIndex(
                                            data_final.FechaAltaCliente).day)) / 30
    data_final.TipoPoblacion = data_final.TipoPoblacion.astype(int) - 1

    Region_dummies = pd.get_dummies(data_final.Region, prefix="Region")
    Gerencia_dummies = pd.get_dummies(data_final.Gerencia, prefix="Gerencia")
    Canales_dummies = pd.get_dummies(data_final.SubCanal, prefix="Canales")
    Estrato_dummies = pd.get_dummies(data_final.Estrato, prefix="Estrato")
    Mes_dummies = pd.get_dummies(data_final.Mes, prefix="Mes")

    data_final = data_final.join(Region_dummies).join(Gerencia_dummies).join(Canales_dummies).join(
        Estrato_dummies).join(Mes_dummies).drop(to_dummies_clients_attr, axis=1)
    return data_final
from src.data.utils import get_train_df
from src.data.utils import get_test_df
from src.data.utils import marca_cupo_sales_df
from src.data.utils import personal_info_sales_df

def main(active_promos_df, executed_promos_df, client_attributes_df, sales_df, test_df, meses_key, CodMes_int):
    marca_cupo_sales = marca_cupo_sales_df(sales_df, meses_key)
    personal_info_sales = personal_info_sales_df(sales_df, meses_key)
    data_train = get_train_df(client_attributes_df, active_promos_df, executed_promos_df
                              , marca_cupo_sales, personal_info_sales)
    data_test = get_test_df(test_df, client_attributes_df, marca_cupo_sales, personal_info_sales, CodMes_int)
    return data_train, data_test
if __name__ == '__main__':
    main()
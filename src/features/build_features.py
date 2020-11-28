from src.features.utils import transform_clients_attr_features

def main(data_final):
    data_final = transform_clients_attr_features(data_final)
    return data_final
if __name__ == '__main__':
    main()
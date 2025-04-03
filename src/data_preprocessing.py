import os
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.path_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger=get_logger(__name__)

class DataPreprocessor:
    def __init__(self, train_path,test_path,processed_dir,config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)

    def preprocessed_data(self,df):
        try:
            logger.info("Starting our Data Preprocessing step")
            logger.info("Dropping the columns")
            df.drop(['Unnamed: 0', 'Booking_ID'],inplace=True,axis=1)
            df.drop_duplicates(inplace=True)

            cat_col=self.config['data_processing']['categorical_columns']
            num_col=self.config['data_processing']['numerical_columns']

            logger.info('Applying Label Encoding')
            le=LabelEncoder()
            mappings={}
            for col in cat_col:
                df[col]=le.fit_transform(df[col])
                mappings[col]={label:code for label,code in zip(le.classes_,le.transform(le.classes_))}
            
            logger.info('Label Mappings are : ')
            for col,mapping in mappings.items():
                logger.info(f'{col} : {mapping}')

            logger.info("Doing Skewness Handling")

            skewness_threshold=self.config['data_processing']['skewness_threshold']
            skewness=df[num_col].apply(lambda x: x.skew())
            for column in skewness[skewness>skewness_threshold].index:
                if skewness[column]>0:
                    df[column]=np.log1p(df[column])
                
            return df
        except Exception as e:
            logger.error(f'Error during preprocess step {e}')
            raise CustomException('Error whlie preprocessing the data',e)
        
    def balanced_data(self,df):
        try:
            logger.info('Handling Imabalance Data')
            x=df.drop('booking_status',axis=1)
            y=df['booking_status']

            smote=SMOTE(random_state=42)
            x_resampled,y_resampled=smote.fit_resample(x,y)

            balanced_df=pd.DataFrame(x_resampled,columns=x.columns)
            balanced_df['booking_status']=y_resampled

            logger.info('Data Balanced Successfully')
            return balanced_df
        except Exception as e:
            logger.error(f'Error during balancing data step {e}')
            raise CustomException('Error while balancing data',e)
        
    def feature_selection(self,df):
        try:
            logger.info('Starting our Feature Selection step')
            x=df.drop('booking_status',axis=1)
            y=df['booking_status']

            model=RandomForestClassifier(random_state=42)
            model.fit(x,y)

            feature_importances=model.feature_importances_
            feature_importances_df=pd.DataFrame({'feature':x.columns,'importance':feature_importances})
            feature_importances_df.sort_values(by='importance',ascending=False,inplace=True)
            number_of_features=self.config['data_processing']['no_of_features']
            selected_features=feature_importances_df.head(number_of_features)['feature'].values
            logger.info(f'Selected Features: {selected_features}')
            logger.info('Feature Selection Completed Successfully')
            return df[selected_features.tolist() + ['booking_status']]
        except Exception as e:
            logger.error(f'Error during feature selection step {e}')
            raise CustomException('Error while feature selection',e)
        
    def save_data(self,df,file_path):
        try:
            logger.info('Saving our Data in preprocessed folder')
            df.to_csv(file_path,index=False)
            logger.info(f'Data Saved Successfully to {file_path}')
        except Exception as e:
            logger.error(f'Error during saving data step {e}')
            raise CustomException('Error while saving data',e)
        
    def process(self):
        try:
            logger.info('Loading data from RAW directory')

            train_df=load_data(self.train_path)
            test_df=load_data(self.test_path)
            
            train_df=self.preprocessed_data(train_df)
            test_df=self.preprocessed_data(test_df)

            train_df=self.balanced_data(train_df)
            test_df=self.balanced_data(test_df)

            train_df=self.feature_selection(train_df)
            test_df=test_df[train_df.columns]

            self.save_data(train_df,PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df,PROCESSED_TEST_DATA_PATH)
            logger.info('Data Preprocessing Completed Successfully')
        except Exception as e:  
            logger.error(f'Error during data preprocessing pipeline {e}')
            raise CustomException('Error while data preprocessing pipeline',e)
        
if __name__=='__main__':
    processor=DataPreprocessor(TRAIN_FILE_PATH,TEST_FILE_PATH,PROCESSED_DIR,CONFIG_PATH)
    processor.process()
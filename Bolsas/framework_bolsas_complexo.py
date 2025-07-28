# framework_bolsas_complexo.py

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import logging

# Ativação do logger para rastreamento detalhado
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Classe de pré-processamento híbrido ---
class PreprocessingModule:
    """
    Módulo responsável pela limpeza, normalização e preparação dos dados.
    Opera de forma híbrida combinando métodos estatísticos e heurísticos simbióticos.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        logging.debug("PreprocessingModule iniciado com StandardScaler.")

    def clean_and_scale(self, df):
        logging.debug("Iniciando limpeza de dados.")
        # Remover linhas com valores ausentes
        df = df.dropna()
        logging.debug(f"Dados após dropna(): {df.shape[0]} linhas restantes.")

        # Normalização apenas colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        logging.debug(f"Colunas numéricas identificadas para escala: {list(numeric_cols)}")

        # Aplicar scaler padrão para normalizar os dados
        df[numeric_cols] = self.scaler.fit_transform(df[numeric_cols])
        logging.debug("Normalização concluída com StandardScaler.")

        return df

# --- Função para indicadores técnicos avançados ---
def compute_advanced_technical_indicators(df):
    """
    Calcula um conjunto expandido de indicadores técnicos para análise financeira,
    incluindo EMA, MACD, RSI, Bandas de Bollinger e VWAP.
    Esta função adiciona colunas diretamente no DataFrame.
    """
    logging.debug("Calculando médias móveis exponenciais (EMA)...")
    df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()

    logging.debug("Calculando MACD e sua linha de sinal...")
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    logging.debug("Calculando RSI (Relative Strength Index)...")
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    logging.debug("Calculando Bandas de Bollinger...")
    df['BB_Mean'] = df['close'].rolling(window=20).mean()
    df['BB_Upper'] = df['BB_Mean'] + 2 * df['close'].rolling(window=20).std()
    df['BB_Lower'] = df['BB_Mean'] - 2 * df['close'].rolling(window=20).std()

    logging.debug("Calculando VWAP (Volume Weighted Average Price)...")
    df['VWAP'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

    logging.debug("Indicadores técnicos calculados e adicionados ao DataFrame.")
    return df

# --- Modelo Deep Learning com LSTM Bidirecional e Atenção ---
class DeepLearningModel:
    """
    Rede neural recorrente com arquitetura LSTM bidirecional, camadas de atenção,
    dropout e batch normalization para previsão de séries temporais financeiras.
    """

    def __init__(self, input_shape):
        logging.debug("Construindo modelo Deep Learning com LSTM bidirecional e atenção.")
        inputs = layers.Input(shape=input_shape)

        # LSTM bidirecional captura dependências temporais passadas e futuras
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True))(inputs)
        x = layers.Bidirectional(layers.LSTM(32, return_sequences=True))(x)

        # Mecanismo de atenção para ponderar features importantes
        attention = layers.Dense(1, activation='tanh')(x)
        attention = layers.Flatten()(attention)
        attention_weights = layers.Activation('softmax')(attention)
        attention_weights = layers.RepeatVector(64)(attention_weights)
        attention_weights = layers.Permute([2, 1])(attention_weights)

        x = layers.Multiply()([x, attention_weights])
        x = layers.Lambda(lambda z: tf.reduce_sum(z, axis=1))(x)

        # Camadas densas com dropout e batch norm para estabilidade
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dense(32, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        x = layers.BatchNormalization()(x)

        outputs = layers.Dense(1)(x)

        self.model = models.Model(inputs=inputs, outputs=outputs)
        self.model.compile(optimizer='adam', loss='mse')

        logging.debug("Modelo Deep Learning compilado com otimizador Adam e perda MSE.")

    def train(self, X_train, y_train, epochs=20, batch_size=32):
        logging.debug(f"Iniciando treinamento do modelo por {epochs} épocas.")
        history = self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)
        logging.debug("Treinamento concluído.")
        return history

    def predict(self, X):
        logging.debug("Gerando previsões com o modelo treinado.")
        preds = self.model.predict(X)
        return preds

# --- Man-in-the-Middle Control para supervisão e filtragem ---
class MitMControl:
    """
    Camada intermediária que intercepta dados e decisões,
    aplica filtros adaptativos, detecta anomalias e ajusta outputs.
    """

    def __init__(self):
        self.logs = []
        logging.debug("MitMControl inicializado com registro de logs.")

    def intercept(self, data):
        logging.debug(f"Interceptando dados com forma {data.shape}.")

        # Filtragem simples: remover previsões fora do intervalo [-3, 3]
        filtered = data[(data >= -3) & (data <= 3)]
        logging.debug(f"Dados filtrados: {filtered.shape[0]} valores mantidos de {data.shape[0]}.")

        # Registro para análise posterior
        self.logs.append(filtered)

        return filtered

# --- Pipeline Completo de Execução ---
def full_pipeline(df):
    logging.info("Iniciando pipeline completo do Framework BOLSAS.")

    # Pré-processamento dos dados
    preproc = PreprocessingModule()
    df_clean = preproc.clean_and_scale(df)

    # Cálculo de indicadores técnicos avançados
    df_indicators = compute_advanced_technical_indicators(df_clean)

    # Remover dados faltantes após cálculo dos indicadores
    df_indicators = df_indicators.dropna()
    logging.debug(f"Dados após dropna pós indicadores: {df_indicators.shape[0]} linhas.")

    # Seleção das features e target para Deep Learning
    feature_cols = ['close', 'EMA_12', 'EMA_26', 'MACD', 'Signal', 'RSI',
                    'BB_Mean', 'BB_Upper', 'BB_Lower', 'VWAP']
    target_col = 'close'

    X = df_indicators[feature_cols].values
    y = df_indicators[target_col].values

    # Preparar para modelo LSTM: reshape para 3D [samples, timesteps, features]
    # Aqui, timestep=1 para simplificação; pode expandir para janelas temporais maiores
    X = X.reshape((X.shape[0], 1, X.shape[1]))

    # Divisão treino/teste
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Instanciar e treinar modelo Deep Learning
    dl_model = DeepLearningModel(input_shape=(X.shape[1], X.shape[2]))
    dl_model.train(X_train, y_train, epochs=20, batch_size=32)

    # Previsões
    preds = dl_model.predict(X_test).flatten()

    # Controle Man-in-the-Middle para filtragem e supervisão
    mitm = MitMControl()
    filtered_preds = mitm.intercept(preds)

    # Métricas de avaliação
    mse = mean_squared_error(y_test[:len(filtered_preds)], filtered_preds)
    mae = mean_absolute_error(y_test[:len(filtered_preds)], filtered_preds)

    logging.info(f"Pipeline concluído - MSE: {mse:.6f}, MAE: {mae:.6f}")

    return filtered_preds, y_test[:len(filtered_preds)]

# --- Exemplo de execução ---
if __name__ == "__main__":
    # Dados simulados para exemplo
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=300)
    close_prices = np.cumsum(np.random.normal(0, 1, 300)) + 100
    volume = np.random.randint(100, 1000, 300)

    df_example = pd.DataFrame({
        'date': dates,
        'close': close_prices,
        'volume': volume
    })

    preds, y_true = full_pipeline(df_example)

    # Exemplo simples de output
    for i in range(min(10, len(preds))):
        logging.info(f"Predição: {preds[i]:.4f} | Valor real: {y_true[i]:.4f}")

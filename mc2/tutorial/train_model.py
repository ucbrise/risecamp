from Utils import FederatedXGBoost

# Instantiate a FederatedXGBoost instance
fxgb = FederatedXGBoost()

# Get number of federating parties
print("Number of parties in federation: ", fxgb.get_num_parties())

# Load training data
training_data_path = "/data/insurance/insurance_training.csv"
fxgb.load_training_data(training_data_path)

# Train a model
params = {'max_depth': 3, "objective": "binary:logistic"}
num_rounds = 100
fxgb.train(params, num_rounds)

# Save the model
fxgb.save_model("ex3_model.model")

# Shutdown
fxgb.shutdown()

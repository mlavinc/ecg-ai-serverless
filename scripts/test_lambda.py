from backend.services.lambda_handler import lambda_handler


event = {
    "record_path": r"C:\Users\mrtne\Projects\ECG_AI_Serverless\ECG_DB\1_Dangerous_VFL_VF\frag\418_C_VFL_277s_frag"
}

response = lambda_handler(
    event,
    None
)

print(response)
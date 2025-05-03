import streamlit_authenticator as stauth

hashed_passwords = stauth.Hasher().hash("boringtradersrocksin2025")

print(hashed_passwords)
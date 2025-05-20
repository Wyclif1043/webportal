from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import random
import string
import hashlib
import json
import base64

WSDL_URL = 'http://krbsc25:7047/BC250/WS/KRB%20SACCO%20TEST/Codeunit/portalService?wsdl'
#http://197.232.170.121:7047/BC240/WS/POLYTECH%20SACCO/Codeunit/PortalWebService
# OPTIONAL: If credentials are needed, insert them here
USERNAME = 'KRBADMIN'  # leave blank if not needed
PASSWORD = 'KRBAdmin@2025'

def get_member_account_statistics(member_no):
    session = Session()

    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        # Call the method directly. Zeep will construct the XML under the hood.
        result = client.service.MemberAccountStatistics(memberNo=member_no)

        # If the return value is a stringified JSON, convert it
        import json
        if isinstance(result, str):
            return json.loads(result)
        return result
    except Exception as e:
        return {'error': str(e)}


def generate_password():
    """Generate a 4-digit numeric password."""
    return ''.join(random.choices('0123456789', k=4))


def register_member(member_no, id_no):
    session = Session()

    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        new_password = generate_password()
        smsport = f"Your one-time pass key is {new_password}. You can change it to your liking."

        result = client.service.fnUpdatePassword(
            memberNo=member_no,
            idNo=id_no,
            newPassword=new_password,  # TEMP PASSWORD = PLAIN TEXT
            smsport=smsport
        )

        return {
            "status": "success",
            "message": "Member registered successfully",
            "temporary_password": new_password,
            "service_response": result
        }

    except Exception as e:
        return {"error": str(e)}



def hash_password(password):
    """Hash the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def change_password(member_number, current_pass, new_pass):
    session = Session()

    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        # Only hash the new password
        hashed_new_pass = hash_password(new_pass)

        result = client.service.fnChangePassword(
            memberNumber=member_number,
            currentPass=current_pass,      # PLAIN
            newPass=hashed_new_pass        # HASHED
        )

        return {
            "status": "success",
            "message": "Password changed successfully",
            "service_response": result
        }
    except Exception as e:
        return {"error": str(e)}


def get_member_profile(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnGetMemberProfile(memberNo=member_no)
        # Example: "92:Mwandary Sidi Elizabeth::Active:0720272284:20500576::110401: ::::06/01/24:::::"
        profile_parts = result.split(":")
        profile_data = {
            "MemberNumber": profile_parts[0],
            "FullName": profile_parts[1],
            "Status": profile_parts[3],
            "Phone": profile_parts[4],
            "IDNumber": profile_parts[5],
            "FosaAccount": profile_parts[7],
            "JoinDate": profile_parts[13] if len(profile_parts) > 13 else ""
        }
        return profile_data
    except Exception as e:
        return {"error": f"Failed to fetch member profile: {str(e)}"}

def get_next_of_kin(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnGetNOKProfile(memberNo=member_no)

        nok_list = []
        if result:
            rows = result.split(";")  # Assuming multiple entries are semicolon-separated
            for row in rows:
                fields = row.split(":")
                if len(fields) >= 4:
                    nok_list.append({
                        "Relationship": fields[0],
                        "Allocation": fields[1],
                        "DateOfBirth": fields[2],
                        "KinName": fields[3]
                    })
        return nok_list
    except Exception as e:
        return {"error": f"Failed to fetch next of kin: {str(e)}"}



def get_member_account_details(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.MemberAccountDetails(memberNo=member_no)
        return json.loads(result)
    except Exception as e:
        return {"error": f"Failed to fetch member account details: {str(e)}"}



def get_loan_guarantors_pdf(member_no, filter_text, big_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnLoanGurantorsReport(
            memberNo=member_no,
            filter=filter_text,
            bigText=big_text
        )

        # The result is a base64-encoded PDF
        pdf_data = base64.b64decode(result)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}


def get_loan_guaranteed_pdf(member_no, filter_text, big_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnLoanGuranteed(
            memberNo=member_no,
            filter=filter_text,
            bigText=big_text
        )

        # The result is a base64-encoded PDF
        pdf_data = base64.b64decode(result)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}


def get_running_loans(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=10)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnRunningLoans(memberNumber=member_no)

        if not result:
            return []

        return json.loads(result)
    except Exception as e:
        return {"error": f"Failed to fetch running loans: {str(e)}"}


def get_member_detailed_statement_pdf(member_no, filter_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnMemberStatement(
            memberNo=member_no,
            filter=filter_text,
        )

        # The result is a base64-encoded PDF
        pdf_data = base64.b64decode(result)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}



def get_member_deposit_statement_pdf(member_no, filter_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnMemberDepositStatement(
            memberNo=member_no,
            filter=filter_text,
        )

        # The result is a base64-encoded PDF
        pdf_data = base64.b64decode(result)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}


def get_loan_statement_pdf(member_no, filter_text, big_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnLoanStatement(
            memberNo=member_no,
            filter=filter_text,
            bigText=big_text
        )

        # 🛠 FIX: Access the base64 content from the SOAP result
        base64_pdf = result.return_value  

        pdf_data = base64.b64decode(base64_pdf)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}

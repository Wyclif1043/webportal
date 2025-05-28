from zeep import Client, Settings
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import random
import string
import hashlib
import json
import base64
import re

WSDL_URL = 'http://197.232.170.121:7047/BC240/WS/Polytech%20Sacco%20Ltd/Codeunit/PortalWebService?wsdl'
#http://krbsc25:7047/BC250/WS/KRB%20SACCO%20TEST/Codeunit/portalService
#http://197.232.170.121:7047/BC240/WS/Polytech%20Sacco%20Ltd/Codeunit/PortalWebService
# OPTIONAL: If credentials are needed, insert them here
USERNAME = 'Swizzsoft'  # leave blank if not needed
PASSWORD = 'Swizzsoft@2024'



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
            newPassword=new_password,
            smsport=smsport
        )

        if result is True:
            return {
                "status": "success",
                "message": "Member registered successfully",
                "temporary_password": new_password,
                "service_response": result
            }
        else:
            return {
                "status": "fail",
                "message": "Member not registered",
                "service_response": result
            }

    except Exception as e:
        return {"error": str(e)}





def hash_password(password):
    """Hash the password using SHA-256 and truncate to 25 chars."""
    full_hash = hashlib.sha256(password.encode()).hexdigest()
    return full_hash[:25]

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


def generate_otp():
    return str(random.randint(1000, 9999))

def send_otp(member_number):
    otp_code = generate_otp()

    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        response = client.service.fnSendOTPCode(memberNumber=member_number, otpCode=otp_code)

        return {
            "message": "OTP sent successfully",
            "otp": otp_code,
            "rawResponse": response
        }

    except Exception as e:
        return {"error": str(e)}


def confirm_otp(member_number, otp_code):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnConfirmOTPCode(memberNumber=member_number, otpCode=otp_code)

        if result is True:
            return {"message": "OTP confirmed successfully"}
        else:
            return {"message": "OTP confirmation failed. wrong  OTP or expired code."}

    except Exception as e:
        return {"error": str(e)}




def hash_password(password):
    """Hash the password using SHA-256 and truncate to 25 chars."""
    full_hash = hashlib.sha256(password.encode()).hexdigest()
    return full_hash[:25]  # Ensure this matches change_password()

def login_member(username, password):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        # Hash the password before sending it to SOAP
        hashed_password = hash_password(password)  # <-- THIS WAS MISSING

        result = client.service.Fnlogin(
            username=username,
            password=hashed_password  # Send the hashed version, not plaintext
        )

        login_success = str(result).strip().lower() == "true"

        return {"authenticated": login_success}

    except Exception as e:
        return {"error": f"Login failed: {str(e)}"}
    

def get_member_account_statistics(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.MemberAccountStatistics(memberNo=member_no)
        raw_json = str(result).strip()

        if not raw_json:
            return {"error": "No data returned"}

        statistics = json.loads(raw_json)
        return statistics

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in SOAP response"}
    except Exception as e:
        return {"error": f"Failed to fetch member account statistics: {str(e)}"}


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


def edit_member_details(member_number, full_names, phone_number, email, id_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnEditMemberDetails(
            memberNumber=member_number,
            fullNames=full_names,
            phoneNumber=phone_number,
            email=email,
            iDNumber=id_number
        )

        return {"success": result}

    except Exception as e:
        return {"error": str(e)}



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


def get_member_detailed_statement_pdf(member_no, filter_text, big_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        soap_response = client.service.fnMemberStatement(
            memberNo=member_no,
            filter=filter_text,
            bigText=big_text
        )

        base64_pdf = soap_response.return_value  
        
        pdf_data = base64.b64decode(base64_pdf)
        return pdf_data

    except Exception as e:
        return {"error": f"Failed to process statement: {str(e)}"}



def get_member_deposit_statement_pdf(member_no, filter_text):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        soap_response = client.service.fnMemberDepositStatement(
            memberNo=member_no,
            filter=filter_text
        )

        print(f"SOAP Response Type: {type(soap_response)}")
        print(f"SOAP Response: {soap_response}")

        if soap_response is None:
            return {"error": "No data returned from SOAP service"}

        if isinstance(soap_response, str):
            base64_data = soap_response
        elif hasattr(soap_response, 'return_value'):
            base64_data = soap_response.return_value
        else:
            return {"error": f"Unexpected response format: {type(soap_response)}"}

        if not base64_data or not base64_data.strip():
            return {"error": "Empty PDF data received"}

        try:
            base64_data = base64_data.strip()
            if len(base64_data) % 4:
                base64_data += '=' * (4 - len(base64_data) % 4)
                
            pdf_data = base64.b64decode(base64_data)
            
            if not pdf_data.startswith(b'%PDF'):
                return {"error": "Returned data is not a valid PDF"}
                
            return pdf_data
            
        except Exception as e:
            return {"error": f"PDF decoding failed: {str(e)}"}

    except Exception as e:
        return {"error": f"SOAP request failed: {str(e)}"}



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

        base64_pdf = result.return_value  

        pdf_data = base64.b64decode(base64_pdf)

        return pdf_data

    except Exception as e:
        return {"error": str(e)}


def get_member_sharecertificate_pdf(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        soap_response = client.service.fnSharesCertificate(
            memberNo=member_no
        )

        if isinstance(soap_response, str):
            base64_pdf = soap_response
            
        elif hasattr(soap_response, 'return_value'):
            base64_pdf = soap_response.return_value
            
        elif isinstance(soap_response, (list, tuple)) and len(soap_response) > 0:
            base64_pdf = soap_response[0]
            
        else:
            return {
                "error": "Unexpected SOAP response format",
                "details": {
                    "response_type": str(type(soap_response)),
                    "response_attrs": dir(soap_response)
                }
            }

        base64_pdf = base64_pdf.strip()
        if not base64_pdf:
            return {"error": "Empty PDF data received"}

        try:
            pdf_data = base64.b64decode(base64_pdf)
            return pdf_data
        except Exception as e:
            return {"error": f"Base64 decoding failed: {str(e)}"}

    except Exception as e:
        return {"error": f"SOAP call failed: {str(e)}"}


# def get_loan_products():
#     session = Session()
#     if USERNAME and PASSWORD:
#         session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

#     transport = Transport(session=session, timeout=30)
#     settings = Settings(strict=False, xml_huge_tree=True)
#     client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

#     try:
#         result = client.service.Fnloanssetup()
#         raw_data = str(result).strip()

#         loan_products = []

#         if raw_data:
#             entries = raw_data.split(":::")
#             for entry in entries:
#                 if ":" in entry:
#                     parts = entry.split(":", 1)
#                     loan_products.append({
#                         "loan_code": parts[0].strip(),
#                         "product_description": parts[1].strip()
#                     })

#         return loan_products

#     except Exception as e:
#         return {"error": str(e)}



# def get_loan_product_details(product_type):
#     session = Session()
#     if USERNAME and PASSWORD:
#         session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

#     transport = Transport(session=session, timeout=30)
#     settings = Settings(strict=False, xml_huge_tree=True)
#     client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

#     try:
#         result = client.service.FnGetLoanProductDetails(productType=product_type)
#         raw_data = result  # Already a string

#         if not raw_data:
#             return {"error": "No data returned from service"}

#         parts = raw_data.split(":::")
#         if len(parts) != 4:
#             return {"error": "Unexpected format in return_value"}

#         return {
#             "minAmount": parts[0].strip(),
#             "maxAmount": parts[1].strip(),
#             "interestRate": parts[2].strip(),
#             "maxInstallments": parts[3].strip()
#         }

#     except Exception as e:
#         return {"error": str(e)}


def get_loan_products_with_details():
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.Fnloanssetup()
        raw_data = result

        loan_products = []
        if raw_data:
            entries = raw_data.split(":::")
            for entry in entries:
                if ":" in entry:
                    parts = entry.split(":", 1)
                    loan_code = parts[0].strip()
                    product_desc = parts[1].strip()

                    try:
                        # Use loan_code as productType
                        details_raw = client.service.FnGetLoanProductDetails(productType=loan_code)

                        if not details_raw:
                            loan_products.append({
                                "loan_code": loan_code,
                                "product_description": product_desc,
                                "error": "No details returned from service"
                            })
                            continue

                        details_parts = details_raw.split(":::")
                        if len(details_parts) == 4:
                            loan_products.append({
                                "loan_code": loan_code,
                                "product_description": product_desc,
                                "minAmount": details_parts[0].strip(),
                                "maxAmount": details_parts[1].strip(),
                                "interestRate": details_parts[2].strip(),
                                "maxInstallments": details_parts[3].strip()
                            })
                        else:
                            loan_products.append({
                                "loan_code": loan_code,
                                "product_description": product_desc,
                                "error": "Unexpected detail format"
                            })
                    except Exception as detail_error:
                        loan_products.append({
                            "loan_code": loan_code,
                            "product_description": product_desc,
                            "error": f"Failed to fetch details: {str(detail_error)}"
                        })

        return loan_products

    except Exception as e:
        return {"error": str(e)}




def apply_for_loan(bosa_no, loan_type, loan_amount, loan_purpose, repayment_period):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        product_details = client.service.FnGetLoanProductDetails(productType=loan_type)
        parts = product_details.split(":::")
        if len(parts) != 4:
            return {"error": "Invalid loan product configuration"}

        min_amount = float(parts[0].replace(",", "").strip())
        max_amount = float(parts[1].replace(",", "").strip())
        max_installments = int(parts[3].strip())

    except Exception as e:
        return {"error": f"Failed to fetch product details: {str(e)}"}

    try:
        loan_amount = float(loan_amount)
        repayment_period = int(repayment_period)
    except:
        return {"error": "Loan amount and repayment period must be valid numbers"}

    if loan_amount < min_amount:
        return {"error": f"Loan amount must be at least {min_amount}"}
    if loan_amount > max_amount:
        return {"error": f"Loan amount must not exceed {max_amount}"}
    if repayment_period > max_installments:
        return {"error": f"Repayment period exceeds max allowed: {max_installments} months"}

    try:
        response = client.service.OnlineLoanApplication(
            bosaNo=bosa_no,
            loanType=loan_type,
            loanAmount=loan_amount,
            loanpurpose=loan_purpose,
            repaymentPeriod=repayment_period
        )

        return {"message": response}

    except Exception as e:
        return {"error": f"Loan application failed: {str(e)}"}


def get_applied_loans(member_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnOnlineLoans(memberNumber=member_no)

        parsed_result = json.loads(result)

        if parsed_result.get("StatusCode") != "200":
            return {"error": "Failed to fetch loans", "details": parsed_result.get("StatusDescription")}

        return parsed_result.get("OnlineLoans", [])

    except Exception as e:
        return {"error": str(e)}


def get_loan_details(member_no, loan_no):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.fnOnlineLoan(
            memberNumber=member_no,
            loanNumber=loan_no
        )

        loan_detail = json.loads(result)

        
        if not loan_detail.get("LoanNo"):
            return {"error": "Loan details not found."}

        return loan_detail

    except Exception as e:
        return {"error": str(e)}


def delete_loan_application(member_number, loan_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.deleteLoanApplication(
            memberNumber=member_number,
            loanNumber=loan_number
        )

        return {"deleted": result}

    except Exception as e:
        return {"error": str(e)}




def edit_online_loan(loan_number, member_number, amount_request, loan_type, repayment_period):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.editOnlineLoan(
            loanNumber=loan_number,
            memberNumber=member_number,
            amountRequest=amount_request,
            loanType=loan_type,
            repaymentPeriod=repayment_period
        )

        if isinstance(result, dict):
            return result

        if isinstance(result, str):
            result = result.strip()
            if result:
                return json.loads(result)
            else:
                return {"error": "Empty response from SOAP service"}

        return {"error": f"Unexpected response type: {type(result)}"}

    except json.JSONDecodeError as json_err:
        return {"error": f"JSON decode error: {str(json_err)}", "raw_result": result}
    except Exception as e:
        return {"error": str(e)}
 
    


def request_guarantorship(member_number, loan_number, amount):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnRequestGuarantorship(
            bosaNo=member_number,  # Correct param name
            loanNumber=loan_number,
            amount=amount
        )

        if str(result).strip().lower() == "true":
            return {"message": "Request sent successfully"}
        else:
            return {"message": "Request not submitted. Cannot add member as guarantor."}

    except Exception as e:
        return {"error": f"Failed to send request guarantorship: {str(e)}"}




def get_loan_guarantors(loan_no, member_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnGetGuarantors(
            loanNo=loan_no,
            memberNumber=member_number
        )

        raw_data = str(result).strip()

        if not raw_data:
            return {"guarantors": []}

        parsed = []
        for g in raw_data.split(":::"):
            g = g.strip()
            if g:
                try:
                    data = json.loads(g)
                    parsed.extend(data.get("OnlineGuarantors", []))
                except json.JSONDecodeError as e:
                    parsed.append({"error": f"Invalid JSON format: {str(e)}", "raw": g})

        return {"guarantors": parsed}

    except Exception as e:
        return {"error": f"Failed to fetch guarantors: {str(e)}"}


def remove_guarantor(member_number, loan_number, guarantor_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.removeGuarantorRequest(
            memberNumber=member_number,
            loanNumber=loan_number,
            guarantorNumber=guarantor_number
        )

        return {"message": "Guarantor removed successfully"}

    except Exception as e:
        return {"error": str(e)}



def get_loans_for_guarantee(member):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnGetLoansForGuarantee(member=member)

        if isinstance(result, dict):
            return result

        result = result.strip()
        if result:
            return json.loads(result)
        else:
            return {"error": "Empty response from SOAP service"}

    except json.JSONDecodeError as json_err:
        return {"error": f"JSON decode error: {str(json_err)}"}
    except Exception as e:
        return {"error": str(e)}


def get_monthly_deduction_details(member_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.FnGetMonthlyDeductionDetails(memberNo=member_number)

        if not result:
            return {"error": "Empty response from service"}

        lines = result.strip().split('\n')
        data = {
            "member": None,
            "monthlyContribution": None,
            "shareCapital": None,
            "loanDeductions": [],
            "summary": {}
        }

        parsing_loans = False
        for line in lines:
            line = line.strip()
            if line.startswith("MEMBER:"):
                data["member"] = line.replace("MEMBER:", "").strip()
            elif line.startswith("Monthly Contribution:"):
                data["monthlyContribution"] = line.replace("Monthly Contribution:", "").strip()
            elif line.startswith("Share Capital:"):
                data["shareCapital"] = line.replace("Share Capital:", "").strip()
            elif line.startswith("LOAN DEDUCTIONS:"):
                parsing_loans = True
            elif parsing_loans and line.startswith("-"):
                # Example: - LN1033 (LT007): INSTANT LOAN - Amount: 21,512
                match = re.match(r"- (.*?) \((.*?)\): (.*?) - Amount: (.*)", line)
                if match:
                    data["loanDeductions"].append({
                        "loanNumber": match.group(1),
                        "loanTypeCode": match.group(2),
                        "loanType": match.group(3),
                        "amount": match.group(4)
                    })
            elif line.startswith("Total Loan Deductions:"):
                data["summary"]["totalLoanDeductions"] = line.replace("Total Loan Deductions:", "").strip()
            elif line.startswith("TOTAL MONTHLY DEDUCTIONS:"):
                data["summary"]["totalMonthlyDeductions"] = line.replace("TOTAL MONTHLY DEDUCTIONS:", "").strip()

        return data

    except Exception as e:
        return {"error": str(e)}




def approve_guarantorship(member_no, loan_no, approved_status):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.ApproveGuarantorship(
            memberNo=member_no,
            loanNo=loan_no,
            approvedStatus=int(approved_status)
        )

        return {"message": "Guarantorship request approved successfully"}

    except Exception as e:
        return {"error": str(e)}


def submit_loan(member_number, loan_number):
    session = Session()
    if USERNAME and PASSWORD:
        session.auth = HTTPBasicAuth(USERNAME, PASSWORD)

    transport = Transport(session=session, timeout=30)
    settings = Settings(strict=False, xml_huge_tree=True)
    client = Client(wsdl=WSDL_URL, transport=transport, settings=settings)

    try:
        result = client.service.SubmitLoan(
            memberNumber=member_number,
            loanNumber=loan_number
        )

        return {"message": "Loan submitted successfully"}

    except Exception as e:
        return {"error": str(e)}

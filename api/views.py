from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .soap_client import get_member_account_statistics
from .soap_client import register_member
from .soap_client import send_otp
from .soap_client import confirm_otp
from .soap_client import login_member
from .soap_client import change_password
from .soap_client import get_member_profile, get_next_of_kin
from .soap_client import edit_member_details
from .soap_client import get_member_account_details
from .soap_client import get_loan_guarantors_pdf
from .soap_client import get_loan_guaranteed_pdf
from .soap_client import get_running_loans
from .soap_client import get_member_detailed_statement_pdf
from .soap_client import get_member_deposit_statement_pdf
from .soap_client import get_loan_statement_pdf
# from .soap_client import get_loan_products
# from .soap_client import get_loan_product_details
from .soap_client import get_loan_products_with_details
from .soap_client import apply_for_loan
from .soap_client import get_applied_loans
from .soap_client import get_loan_details
from .soap_client import delete_loan_application
from .soap_client import edit_online_loan
from .soap_client import request_guarantorship
from .soap_client import get_loan_guarantors
from .soap_client import get_member_sharecertificate_pdf
from .soap_client import get_loans_for_guarantee
from .soap_client import approve_guarantorship
from .soap_client import remove_guarantor
from .soap_client import submit_loan
from .soap_client import get_monthly_deduction_details


class MemberAccountStatisticsView(APIView):
    def get(self, request):
        member_no = request.query_params.get("member_no")

        if not member_no:
            return Response({"error": "member_no is required"}, status=400)

        result = get_member_account_statistics(member_no)

        if "error" in result:
            return Response(result, status=500)

        return Response(result)



class RegisterMemberView(APIView):
    def post(self, request):
        member_no = request.data.get("member_no")
        id_no = request.data.get("id_no")

        if not member_no or not id_no:
            return Response({"error": "member_no and id_no are required"}, status=status.HTTP_400_BAD_REQUEST)

        data = register_member(member_no, id_no)

        if 'error' in data:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    def post(self, request):
        member_no = request.data.get("member_no")
        current_pass = request.data.get("current_pass")
        new_pass = request.data.get("new_pass")

        if not member_no or not current_pass or not new_pass:
            return Response({"error": "member_no, current_pass, and new_pass are required"}, status=status.HTTP_400_BAD_REQUEST)

        data = change_password(member_no, current_pass, new_pass)

        if 'error' in data:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data, status=status.HTTP_200_OK)

class SendOTPView(APIView):
    def post(self, request):
        member_number = request.data.get("memberNumber")

        if not member_number:
            return Response({"error": "Member number is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = send_otp(member_number)

        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)


class ConfirmOTPView(APIView):
    def post(self, request):
        member_number = request.data.get("memberNumber")
        otp_code = request.data.get("otpCode")

        if not member_number or not otp_code:
            return Response({"error": "memberNumber and otpCode are required"}, status=status.HTTP_400_BAD_REQUEST)

        result = confirm_otp(member_number, otp_code)

        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)




class MemberLoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        result = login_member(username, password)

        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if result.get("authenticated"):
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)



class MemberProfileView(APIView):
    def get(self, request):
        member_no = request.query_params.get("member_no")
        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        profile = get_member_profile(member_no)
        if "error" in profile:
            return Response(profile, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        nok = get_next_of_kin(member_no)
        if "error" in nok:
            return Response(nok, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "profile": profile,
            "next_of_kin": nok
        })


class EditMemberDetailsView(APIView):
    def post(self, request):
        data = request.data
        member_number = data.get("memberNumber")
        full_names = data.get("fullNames")
        phone_number = data.get("phoneNumber")
        email = data.get("email")
        id_number = data.get("iDNumber")

        if not all([member_number, full_names, phone_number, email, id_number]):
            return Response({"error": "All fields are required."}, status=400)

        result = edit_member_details(member_number, full_names, phone_number, email, id_number)

        if "error" in result:
            return Response(result, status=500)

        return Response(result, status=200)




class MemberAccountDetailsView(APIView):
    def get(self, request):
        member_no = request.query_params.get("member_no")
        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        details = get_member_account_details(member_no)
        if "error" in details:
            return Response(details, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(details)

class LoanGuarantorsReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')
        big_text = request.query_params.get('big_text', '')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_loan_guarantors_pdf(member_no, filter_text, big_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="loan_guaranteed_{member_no}.pdf"'
        return response
    

class LoanGuaranteedReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')
        big_text = request.query_params.get('big_text', '')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_loan_guaranteed_pdf(member_no, filter_text, big_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="loan_guaranteed_{member_no}.pdf"'
        return response
    

class MemberRunningLoansView(APIView):
    def get(self, request):
        member_no = request.query_params.get("member_no")
        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        loans = get_running_loans(member_no)
        if isinstance(loans, dict) and "error" in loans:
            return Response(loans, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(loans)


class MemberDetailedReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')
        big_text = request.query_params.get('big_text', '')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_member_detailed_statement_pdf(member_no, filter_text, big_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="member_detailed_{member_no}.pdf"'
        return response




class MemberDepositReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')

        if not member_no:
            return Response(
                {"error": "member_no is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = get_member_deposit_statement_pdf(member_no, filter_text)
        
        if isinstance(result, dict) and "error" in result:
            return Response(
                result,
                status=status.HTTP_502_BAD_GATEWAY
            )

        response = HttpResponse(result, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="deposit_statement_{member_no}.pdf"'
        )
        return response


class MemberShareCertificateView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        
        if not member_no:
            return Response(
                {"error": "member_no is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = get_member_sharecertificate_pdf(member_no)
        
        if isinstance(result, dict) and "error" in result:
            return Response(
                result,
                status=status.HTTP_502_BAD_GATEWAY  
            )

        response = HttpResponse(result, content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="share_certificate_{member_no}.pdf"'
        )
        return response


class LoanStatementReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')
        big_text = request.query_params.get('big_text', '')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_loan_statement_pdf(member_no, filter_text, big_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="loan_statement_{member_no}.pdf"'
        return response


# class LoanProductsView(APIView):
#     def get(self, request):
#         data = get_loan_products()

#         if isinstance(data, dict) and "error" in data:
#             return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(data, status=status.HTTP_200_OK)
    

# class LoanProductDetailView(APIView):
#     def get(self, request):
#         product_type = request.query_params.get("product_type")

#         if not product_type:
#             return Response({"error": "product_type is required"}, status=400)

#         details = get_loan_product_details(product_type)

#         if "error" in details:
#             return Response(details, status=500)

#         return Response(details)


class LoanProductsView(APIView):
    def get(self, request):
        data = get_loan_products_with_details()

        if isinstance(data, dict) and "error" in data:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)
    
class ApplyLoanView(APIView):
    def post(self, request):
        data = request.data
        bosa_no = data.get("bosa_no")
        loan_type = data.get("loan_type")
        loan_amount = data.get("loan_amount")
        loan_purpose = data.get("loan_purpose")
        repayment_period = data.get("repayment_period")

        if not all([bosa_no, loan_type, loan_amount, loan_purpose, repayment_period]):
            return Response({"error": "All fields are required"}, status=400)

        result = apply_for_loan(bosa_no, loan_type, loan_amount, loan_purpose, repayment_period)

        if "error" in result:
            return Response(result, status=400)

        return Response(result)


class AppliedLoansView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        loans = get_applied_loans(member_no)

        if isinstance(loans, dict) and "error" in loans:
            return Response(loans, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"loans": loans}, status=status.HTTP_200_OK)


class LoanDetailsView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        loan_no = request.query_params.get('loan_no')

        if not member_no or not loan_no:
            return Response(
                {"error": "Both 'member_no' and 'loan_no' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        loan_detail = get_loan_details(member_no, loan_no)

        if isinstance(loan_detail, dict) and "error" in loan_detail:
            return Response(loan_detail, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(loan_detail, status=status.HTTP_200_OK)


class DeleteLoanApplicationView(APIView):
    def post(self, request):
        member_number = request.data.get("memberNumber")
        loan_number = request.data.get("loanNumber")

        if not member_number or not loan_number:
            return Response({"error": "memberNumber and loanNumber are required"}, status=400)

        result = delete_loan_application(member_number, loan_number)

        if "error" in result:
            return Response(result, status=500)

        if not result.get("deleted"):
            return Response({"error": "Loan could not be deleted"}, status=400)

        return Response({"message": "Loan deleted successfully"})



class EditOnlineLoanView(APIView):
    def post(self, request):
        data = request.data
        required_fields = ["loanNumber", "memberNumber", "amountRequest", "loanType", "repaymentPeriod"]

        missing = [field for field in required_fields if field not in data]
        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)

        result = edit_online_loan(
            loan_number=data["loanNumber"],
            member_number=data["memberNumber"],
            amount_request=data["amountRequest"],
            loan_type=data["loanType"],
            repayment_period=data["repaymentPeriod"]
        )

        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)
    


class RequestGuarantorshipView(APIView):
    def post(self, request):
        member_number = request.data.get("member_number")
        loan_number = request.data.get("loan_number")
        amount = request.data.get("amount")

        if not member_number or not loan_number or not amount:
            return Response({"error": "member_number, loan_number and amount are required."}, status=400)

        result = request_guarantorship(member_number, loan_number, amount)

        if "error" in result:
            return Response(result, status=500)

        return Response(result)

class RemoveGuarantorView(APIView):
    def post(self, request):
        data = request.data
        member_number = data.get("memberNumber")
        loan_number = data.get("loanNumber")
        guarantor_number = data.get("guarantorNumber")

        if not all([member_number, loan_number, guarantor_number]):
            return Response({"error": "memberNumber, loanNumber, and guarantorNumber are required"}, status=400)

        result = remove_guarantor(member_number, loan_number, guarantor_number)

        if "error" in result:
            return Response(result, status=500)

        return Response(result, status=200)
    


class GetLoanGuarantorsView(APIView):
    def get(self, request):
        loan_no = request.query_params.get("loan_no")
        member_number = request.query_params.get("member_number")

        if not loan_no or not member_number:
            return Response({"error": "loan_no and member_number are required."}, status=400)

        result = get_loan_guarantors(loan_no, member_number)

        if "error" in result:
            return Response(result, status=500)

        return Response(result)


class LoansForGuaranteeView(APIView):
    def get(self, request):
        member = request.query_params.get('member')

        if not member:
            return Response({"error": "member is required"}, status=status.HTTP_400_BAD_REQUEST)

        result = get_loans_for_guarantee(member)

        if isinstance(result, dict) and "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)



class ApproveGuarantorshipView(APIView):
    def post(self, request):
        data = request.data
        member_no = data.get("memberNo")
        loan_no = data.get("loanNo")
        approved_status = data.get("approvedStatus")

        if not all([member_no, loan_no, approved_status in ["0", "1", 0, 1]]):
            return Response({"error": "memberNo, loanNo, and approvedStatus (0 or 1) are required"}, status=400)

        result = approve_guarantorship(member_no, loan_no, approved_status)

        if "error" in result:
            return Response(result, status=500)

        return Response(result, status=200)


class MonthlyDeductionDetailsView(APIView):
    def post(self, request):
        member_number = request.data.get("memberNumber")

        if not member_number:
            return Response({"error": "memberNumber is required"}, status=400)

        result = get_monthly_deduction_details(member_number)

        if "error" in result:
            return Response(result, status=500)

        return Response(result, status=200)


class SubmitLoanView(APIView):
    def post(self, request):
        member_number = request.data.get("memberNumber")
        loan_number = request.data.get("loanNumber")

        if not member_number or not loan_number:
            return Response({"error": "memberNumber and loanNumber are required"}, status=400)

        result = submit_loan(member_number, loan_number)

        if "error" in result:
            return Response(result, status=500)

        return Response(result, status=200)
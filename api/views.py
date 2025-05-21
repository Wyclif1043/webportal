from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .soap_client import get_member_account_statistics
from .soap_client import register_member
from .soap_client import change_password
from .soap_client import get_member_profile, get_next_of_kin
from .soap_client import get_member_account_details
from .soap_client import get_loan_guarantors_pdf
from .soap_client import get_loan_guaranteed_pdf
from .soap_client import get_running_loans
from .soap_client import get_member_detailed_statement_pdf
from .soap_client import get_member_deposit_statement_pdf
from .soap_client import get_loan_statement_pdf
from .soap_client import get_loan_products
from .soap_client import get_loan_product_details
from .soap_client import apply_for_loan
from .soap_client import get_online_applied_loans
from .soap_client import request_guarantorship
from .soap_client import edit_online_loan
from .soap_client import get_loan_guarantors



class MemberStatsView(APIView):
    def get(self, request, member_no):
        data = get_member_account_statistics(member_no)
        if 'error' in data:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data, status=status.HTTP_200_OK)

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
        response['Content-Disposition'] = f'attachment; filename="loan_guarantors_{member_no}.pdf"'
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
        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_member_detailed_statement_pdf(member_no, filter_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="detailed_statement_{member_no}.pdf"'
        return response


class MemberDepositReportView(APIView):
    def get(self, request):
        member_no = request.query_params.get('member_no')
        filter_text = request.query_params.get('filter', '')

        if not member_no:
            return Response({"error": "member_no is required"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_data = get_member_deposit_statement_pdf(member_no, filter_text)

        if isinstance(pdf_data, dict) and "error" in pdf_data:
            return Response(pdf_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="member_deposit_{member_no}.pdf"'
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


class LoanProductsView(APIView):
    def get(self, request):
        data = get_loan_products()

        if isinstance(data, dict) and "error" in data:
            return Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(data, status=status.HTTP_200_OK)
    

class LoanProductDetailView(APIView):
    def get(self, request):
        product_type = request.query_params.get("product_type")

        if not product_type:
            return Response({"error": "product_type is required"}, status=400)

        details = get_loan_product_details(product_type)

        if "error" in details:
            return Response(details, status=500)

        return Response(details)
    
class ApplyLoanView(APIView):
    def post(self, request):
        data = request.data
        bosa_no = data.get("bosa_no")
        loan_type = data.get("loan_type")
        loan_amount = data.get("loan_amount")
        loan_purpose = data.get("loan_purpose")
        repayment_period = data.get("repayment_period")

        # Required field check
        if not all([bosa_no, loan_type, loan_amount, loan_purpose, repayment_period]):
            return Response({"error": "All fields are required"}, status=400)

        result = apply_for_loan(bosa_no, loan_type, loan_amount, loan_purpose, repayment_period)

        if "error" in result:
            return Response(result, status=400)

        return Response(result)


class OnlineLoansView(APIView):
    def get(self, request):
        member_no = request.query_params.get("member_no")
        if not member_no:
            return Response({"error": "member_no is required"}, status=400)

        result = get_online_applied_loans(member_no)

        if "error" in result:
            return Response(result, status=500)

        return Response(result)

class EditOnlineLoanView(APIView):
    def post(self, request):
        loan_number = request.data.get("loan_number")
        member_number = request.data.get("member_number")
        amount_requested = request.data.get("amount_requested")
        loan_type = request.data.get("loan_type")
        repayment_period = request.data.get("repayment_period")

        if not all([loan_number, member_number, amount_requested, loan_type, repayment_period]):
            return Response({"error": "All fields are required."}, status=400)

        try:
            amount_requested = float(amount_requested)
            repayment_period = int(repayment_period)
        except ValueError:
            return Response({"error": "Invalid numeric values for amount_requested or repayment_period."}, status=400)

        result = edit_online_loan(
            loan_number, member_number, amount_requested, loan_type, repayment_period
        )

        if "error" in result:
            return Response(result, status=500)

        return Response(result)


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

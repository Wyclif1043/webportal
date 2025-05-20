from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .soap_client import get_member_account_statistics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .soap_client import register_member
from .soap_client import change_password
from .soap_client import get_member_profile, get_next_of_kin
from .soap_client import get_member_account_details
from django.http import HttpResponse
from .soap_client import get_loan_guarantors_pdf
from .soap_client import get_loan_guaranteed_pdf
from .soap_client import get_running_loans
from .soap_client import get_member_detailed_statement_pdf
from .soap_client import get_member_deposit_statement_pdf
from .soap_client import get_loan_statement_pdf


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
        return Response(data, status=status.HTTP_200_OK)# Create your views here.


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
    
from django.urls import path
from .views import MemberStatsView
from .views import MemberStatsView, RegisterMemberView
from .views import ChangePasswordView
from .views import MemberProfileView
from .views import MemberAccountDetailsView
from .views import LoanGuarantorsReportView
from .views import LoanGuaranteedReportView
from .views import MemberRunningLoansView
from .views import MemberDetailedReportView
from .views import MemberDepositReportView
from .views import LoanStatementReportView
from .views import LoanProductsView
from .views import LoanProductDetailView
from .views import ApplyLoanView
from .views import OnlineLoansView
from .views import RequestGuarantorshipView
from .views import EditOnlineLoanView
from .views import GetLoanGuarantorsView


urlpatterns = [
    path('member-stats/<str:member_no>/', MemberStatsView.as_view(), name='member-stats'),
    path('register-member/', RegisterMemberView.as_view(), name='register-member'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('member-profile/', MemberProfileView.as_view(), name='member-profile'),
    path('member-account-details/', MemberAccountDetailsView.as_view(), name='member-account-details'),
    path('loan-guaranteed-report/', LoanGuarantorsReportView.as_view(), name='loan-guarantors-report'),
    path('loan-guarantors-report/', LoanGuaranteedReportView.as_view(), name='loan-guaranteed-report'),
    path('member-running-loans/', MemberRunningLoansView.as_view(), name='member-running-loans'),
    path('member-detailed-report/', MemberDetailedReportView.as_view(), name='member-detailed-report'),
    path('member-deposit-report/', MemberDepositReportView.as_view(), name='member-deposit-report'),
    path('loan-statement-report/', LoanStatementReportView.as_view(), name='loan-statement-report'),
    path('loan-products/', LoanProductsView.as_view(), name='loan-products'),
    path('loan-product-details/', LoanProductDetailView.as_view(), name='loan-product-details'),
    path('apply-loan/', ApplyLoanView.as_view(), name='apply-loan'),
    path('online-loans/', OnlineLoansView.as_view(), name='online-loans'),
    path('request-guarantorship/', RequestGuarantorshipView.as_view(), name='request-guarantorship'),
    path('edit-online-loan/', EditOnlineLoanView.as_view(), name='edit-online-loan'),
    path('get-loan-guarantors/', GetLoanGuarantorsView.as_view(), name='get-loan-guarantors'),
]

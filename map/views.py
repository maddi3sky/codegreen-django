from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import DataPoint, Comment, UserMark, Site, Pledge
from .serializers import DataPointSerializer, CommentSerializer, UserMarkSerializer, PledgeSerializer


def index(request):
    return render(request, 'map/index.html', {
        'user': request.user,
        'is_authenticated': request.user.is_authenticated,
        'display_name': request.user.get_full_name() or request.user.email if request.user.is_authenticated else '',
    })


# ── NDVI Data ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ndvi_data(request, site_id, year):
    points = DataPoint.objects.filter(site_id=site_id, year=year).values('lat', 'lng', 'ndvi')
    return Response(list(points))


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ndvi_all_years(request, site_id):
    """Return all years for a site as {year: [{lat,lng,ndvi},...]} — loaded once on page init."""
    years = DataPoint.objects.filter(site_id=site_id).values_list('year', flat=True).distinct()
    data = {}
    for yr in sorted(years):
        pts = list(DataPoint.objects.filter(site_id=site_id, year=yr).values('lat', 'lng', 'ndvi'))
        data[yr] = pts
    return Response(data)


# ── Comments ───────────────────────────────────────────────────────────────────

class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = Comment.objects.all()
        site_id = self.kwargs.get('site_id')
        year = self.kwargs.get('year')
        if site_id:
            qs = qs.filter(site_id=site_id)
        if year:
            qs = qs.filter(year=year)
        return qs

    def perform_create(self, serializer):
        site_id = self.kwargs.get('site_id', 'wilmington')
        year = self.kwargs.get('year', 2025)
        user = self.request.user if self.request.user.is_authenticated else None
        author = user.get_full_name() or user.email if user else serializer.validated_data.get('author', 'Anonymous')
        serializer.save(site_id=site_id, year=year, user=user, author=author)


# ── User Marks ─────────────────────────────────────────────────────────────────

class UserMarkList(generics.ListCreateAPIView):
    serializer_class = UserMarkSerializer

    def get_queryset(self):
        site_id = self.request.query_params.get('site', 'wilmington')
        return UserMark.objects.filter(site_id=site_id)

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        session_key = self.request.session.session_key or ''
        serializer.save(user=user, session_key=session_key)


# ── Pledges ────────────────────────────────────────────────────────────────────

class PledgeList(generics.ListCreateAPIView):
    serializer_class = PledgeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        site_id = self.request.query_params.get('site', 'wilmington')
        return Pledge.objects.filter(site_id=site_id)

    def perform_create(self, serializer):
        site_id = self.request.data.get('site_id', 'wilmington')
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(site_id=site_id, user=user)


# ── Auth Status ────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bug_report(request):
    from .models import BugReport
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'error': 'text required'}, status=400)
    BugReport.objects.create(
        text=text,
        contact=request.data.get('contact', ''),
        site=request.data.get('site', ''),
        url=request.data.get('url', ''),
    )
    return Response({'ok': True})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_status(request):
    if request.user.is_authenticated:
        return Response({
            'authenticated': True,
            'name': request.user.get_full_name() or request.user.email,
            'email': request.user.email,
        })
    return Response({'authenticated': False})

import unittest

from django.conf.urls import include, url
from django.test import TestCase, override_settings

from rest_framework import filters, pagination, permissions, serializers
from rest_framework.compat import coreapi
from rest_framework.decorators import detail_route, list_route
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import SchemaGenerator
from rest_framework.test import APIClient
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


class MockUser(object):
    def is_authenticated(self):
        return True


class ExamplePagination(pagination.PageNumberPagination):
    page_size = 100


class EmptySerializer(serializers.Serializer):
    pass


class ExampleSerializer(serializers.Serializer):
    a = serializers.CharField(required=True, help_text='A field description')
    b = serializers.CharField(required=False)
    read_only = serializers.CharField(read_only=True)
    hidden = serializers.HiddenField(default='hello')


class AnotherSerializer(serializers.Serializer):
    c = serializers.CharField(required=True)
    d = serializers.CharField(required=False)


class ExampleViewSet(ModelViewSet):
    pagination_class = ExamplePagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    serializer_class = ExampleSerializer

    @detail_route(methods=['post'], serializer_class=AnotherSerializer)
    def custom_action(self, request, pk):
        return super(ExampleSerializer, self).retrieve(self, request)

    @list_route()
    def custom_list_action(self, request):
        return super(ExampleViewSet, self).list(self, request)

    @list_route(methods=['post', 'get'], serializer_class=EmptySerializer)
    def custom_list_action_multiple_methods(self, request):
        return super(ExampleViewSet, self).list(self, request)

    def get_serializer(self, *args, **kwargs):
        assert self.request
        assert self.action
        return super(ExampleViewSet, self).get_serializer(*args, **kwargs)


router = DefaultRouter(schema_title='Example API' if coreapi else None)
router.register('example', ExampleViewSet, base_name='example')
urlpatterns = [
    url(r'^', include(router.urls))
]


@unittest.skipUnless(coreapi, 'coreapi is not installed')
@override_settings(ROOT_URLCONF='tests.test_schemas')
class TestRouterGeneratedSchema(TestCase):
    def test_anonymous_request(self):
        client = APIClient()
        response = client.get('/', HTTP_ACCEPT='application/vnd.coreapi+json')
        self.assertEqual(response.status_code, 200)
        expected = coreapi.Document(
            url='',
            title='Example API',
            content={
                'example': {
                    'list': coreapi.Link(
                        url='/example/',
                        action='get',
                        fields=[
                            coreapi.Field('page', required=False, location='query'),
                            coreapi.Field('ordering', required=False, location='query')
                        ]
                    ),
                    'custom_list_action': coreapi.Link(
                        url='/example/custom_list_action/',
                        action='get'
                    ),
                    'custom_list_action_multiple_methods': {
                        'read': coreapi.Link(
                            url='/example/custom_list_action_multiple_methods/',
                            action='get'
                        )
                    },
                    'read': coreapi.Link(
                        url='/example/{pk}/',
                        action='get',
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    )
                }
            }
        )
        self.assertEqual(response.data, expected)

    def test_authenticated_request(self):
        client = APIClient()
        client.force_authenticate(MockUser())
        response = client.get('/', HTTP_ACCEPT='application/vnd.coreapi+json')
        self.assertEqual(response.status_code, 200)
        expected = coreapi.Document(
            url='',
            title='Example API',
            content={
                'example': {
                    'list': coreapi.Link(
                        url='/example/',
                        action='get',
                        fields=[
                            coreapi.Field('page', required=False, location='query'),
                            coreapi.Field('ordering', required=False, location='query')
                        ]
                    ),
                    'create': coreapi.Link(
                        url='/example/',
                        action='post',
                        encoding='application/json',
                        fields=[
                            coreapi.Field('a', required=True, location='form', description='A field description'),
                            coreapi.Field('b', required=False, location='form')
                        ]
                    ),
                    'read': coreapi.Link(
                        url='/example/{pk}/',
                        action='get',
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    ),
                    'custom_action': coreapi.Link(
                        url='/example/{pk}/custom_action/',
                        action='post',
                        encoding='application/json',
                        fields=[
                            coreapi.Field('pk', required=True, location='path'),
                            coreapi.Field('c', required=True, location='form'),
                            coreapi.Field('d', required=False, location='form'),
                        ]
                    ),
                    'custom_list_action': coreapi.Link(
                        url='/example/custom_list_action/',
                        action='get'
                    ),
                    'custom_list_action_multiple_methods': {
                        'read': coreapi.Link(
                            url='/example/custom_list_action_multiple_methods/',
                            action='get'
                        ),
                        'create': coreapi.Link(
                            url='/example/custom_list_action_multiple_methods/',
                            action='post'
                        )
                    },
                    'update': coreapi.Link(
                        url='/example/{pk}/',
                        action='put',
                        encoding='application/json',
                        fields=[
                            coreapi.Field('pk', required=True, location='path'),
                            coreapi.Field('a', required=True, location='form', description='A field description'),
                            coreapi.Field('b', required=False, location='form')
                        ]
                    ),
                    'partial_update': coreapi.Link(
                        url='/example/{pk}/',
                        action='patch',
                        encoding='application/json',
                        fields=[
                            coreapi.Field('pk', required=True, location='path'),
                            coreapi.Field('a', required=False, location='form', description='A field description'),
                            coreapi.Field('b', required=False, location='form')
                        ]
                    ),
                    'delete': coreapi.Link(
                        url='/example/{pk}/',
                        action='delete',
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    )
                }
            }
        )
        self.assertEqual(response.data, expected)


class ExampleListView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class ExampleDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, *args, **kwargs):
        pass


@unittest.skipUnless(coreapi, 'coreapi is not installed')
class TestSchemaGenerator(TestCase):
    def setUp(self):
        self.patterns = [
            url('^example/?$', ExampleListView.as_view()),
            url('^example/(?P<pk>\d+)/?$', ExampleDetailView.as_view()),
            url('^example/(?P<pk>\d+)/sub/?$', ExampleDetailView.as_view()),
        ]

    def test_schema_for_regular_views(self):
        """
        Ensure that schema generation works for APIView classes.
        """
        generator = SchemaGenerator(title='Example API', patterns=self.patterns)
        schema = generator.get_schema()
        expected = coreapi.Document(
            url='',
            title='Example API',
            content={
                'example': {
                    'create': coreapi.Link(
                        url='/example/',
                        action='post',
                        fields=[]
                    ),
                    'list': coreapi.Link(
                        url='/example/',
                        action='get',
                        fields=[]
                    ),
                    'read': coreapi.Link(
                        url='/example/{pk}/',
                        action='get',
                        fields=[
                            coreapi.Field('pk', required=True, location='path')
                        ]
                    ),
                    'sub': {
                        'list': coreapi.Link(
                            url='/example/{pk}/sub/',
                            action='get',
                            fields=[
                                coreapi.Field('pk', required=True, location='path')
                            ]
                        )
                    }
                }
            }
        )
        self.assertEqual(schema, expected)

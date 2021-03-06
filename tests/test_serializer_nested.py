from django.http import QueryDict

from rest_framework import serializers


class TestNestedSerializer:
    def setup(self):
        class NestedSerializer(serializers.Serializer):
            one = serializers.IntegerField(max_value=10)
            two = serializers.IntegerField(max_value=10)

        class TestSerializer(serializers.Serializer):
            nested = NestedSerializer()

        self.Serializer = TestSerializer

    def test_nested_validate(self):
        input_data = {
            'nested': {
                'one': '1',
                'two': '2',
            }
        }
        expected_data = {
            'nested': {
                'one': 1,
                'two': 2,
            }
        }
        serializer = self.Serializer(data=input_data)
        assert serializer.is_valid()
        assert serializer.validated_data == expected_data

    def test_nested_serialize_empty(self):
        expected_data = {
            'nested': {
                'one': None,
                'two': None
            }
        }
        serializer = self.Serializer()
        assert serializer.data == expected_data


class TestNotRequiredNestedSerializer:
    def setup(self):
        class NestedSerializer(serializers.Serializer):
            one = serializers.IntegerField(max_value=10)

        class TestSerializer(serializers.Serializer):
            nested = NestedSerializer(required=False)

        self.Serializer = TestSerializer

    def test_json_validate(self):
        input_data = {}
        serializer = self.Serializer(data=input_data)
        assert serializer.is_valid()

        input_data = {'nested': {'one': '1'}}
        serializer = self.Serializer(data=input_data)
        assert serializer.is_valid()

    def test_multipart_validate(self):
        input_data = QueryDict('')
        serializer = self.Serializer(data=input_data)
        assert serializer.is_valid()

        input_data = QueryDict('nested[one]=1')
        serializer = self.Serializer(data=input_data)
        assert serializer.is_valid()


class TestNestedSerializerWithMany:
    def setup(self):
        class NestedSerializer(serializers.Serializer):
            example = serializers.IntegerField(max_value=10)

        class TestSerializer(serializers.Serializer):
            allow_null = NestedSerializer(many=True, allow_null=True)
            not_allow_null = NestedSerializer(many=True)

        self.Serializer = TestSerializer

    def test_null_allowed_if_allow_null_is_set(self):
        input_data = {
            'allow_null': None,
            'not_allow_null': [{'example': '2'}, {'example': '3'}]
        }
        expected_data = {
            'allow_null': None,
            'not_allow_null': [{'example': 2}, {'example': 3}]
        }
        serializer = self.Serializer(data=input_data)

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data == expected_data

    def test_null_is_not_allowed_if_allow_null_is_not_set(self):
        input_data = {
            'allow_null': None,
            'not_allow_null': None
        }
        serializer = self.Serializer(data=input_data)

        assert not serializer.is_valid()

        expected_errors = {'not_allow_null': [serializer.error_messages['null']]}
        assert serializer.errors == expected_errors

    def test_run_the_field_validation_even_if_the_field_is_null(self):
        class TestSerializer(self.Serializer):
            validation_was_run = False

            def validate_allow_null(self, value):
                TestSerializer.validation_was_run = True
                return value

        input_data = {
            'allow_null': None,
            'not_allow_null': [{'example': 2}]
        }
        serializer = TestSerializer(data=input_data)

        assert serializer.is_valid()
        assert serializer.validated_data == input_data
        assert TestSerializer.validation_was_run

from rest_framework import viewsets, mixins

class RetrieveUpdateCreateListViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
    Un viewset offrant les methode par defaut `create()`, `retrieve()`, `update()`,
    `partial_update()`, et `list()`.
    """
    pass

class RetrieveUpdateListViewSet(
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    
    pass

class UpdateViewSet(
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    
    pass


class RetrieveListViewSet(
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    
    pass

class CreateViewSet(
                   mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    pass

class ListViewSet(
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    pass

class RetrieveUpdateViewSet(
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   viewsets.GenericViewSet):
    pass
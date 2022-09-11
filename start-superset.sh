helm repo update \
&& helm upgrade \
    --install \
    --values helm_chart_values/superset-values.yml \
    --namespace superset \
    --create-namespace \
    superset \
    superset/superset

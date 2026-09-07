{{/*
Expand the name of the chart.
*/}}
{{- define "task-platform.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "task-platform.labels" -}}
app.kubernetes.io/name: {{ include "task-platform.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/part-of: task-platform
{{- end }}

{{/*
Selector labels
*/}}
{{- define "task-platform.selectorLabels" -}}
app.kubernetes.io/name: {{ include "task-platform.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


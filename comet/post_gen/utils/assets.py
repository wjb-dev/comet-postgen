# assets.py  ← drop this next to utils/, purge.py, etc.
from comet.art.ascii.assets import *

LANGUAGE_ASSETS = [
    {
        "language": "go",
        "files": [
            "Dockerfile",
            "Makefile",
            "Makefile.cpp",
            "README.md",
            "go.mod",
            "skaffold.yaml",
            "configs/dev.yaml",
            "configs/prod.yaml",
            "internal/config/config.go",
            "internal/handler/echo.go",
            "internal/handler/ping.go",
            "internal/server/health.go",
            "internal/server/server.go",
            "pkg/proto/v1/ping.proto",
            "pkg/proto/v1/service.proto",
            # "cmd/{{ cookiecutter.project_slug }}/main.go",
            "test/integration/echo_integration_test.go",
            "test/integration/health_integration_test.go",
            "test/integration/ping_integration_test.go",
            "test/integration/testutil.go",
            "test/unit/config/config_test.go",
            "test/unit/handler/echo_test.go",
            "test/unit/handler/ping_test.go",
            "test/unit/server/health_test.go",
            "test/unit/server/server_test.go",
            "test/unit_test.go",
            "test/package.go",
            "runConfigurations/go/Golang.run.xml",
            "chart/Chart.yaml",
            "chart/templates/deployment.yaml",
            "chart/templates/service.yaml",
            "chart/templates/_helpers.tpl",
            "chart/values.yaml",
            "infra/terraform/main.tf",
            "src/cpp/CMakeLists.txt",
            "src/cpp/main.cc",
            "tests/cpp/test_stub.cc"
        ],
        "dirs": [
            "cmd/",
            "configs/",
            "internal/",
            "internal/config/",
            "internal/handler/",
            "internal/server/",
            "pkg/",
            "pkg/proto/",
            "pkg/proto/v1/",
            "test/",
            "test/integration/",
            "test/unit/",
            "test/unit/config/",
            "test/unit/handler/",
            "test/unit/server/",
            "runConfigurations/",
            "runConfigurations/go/",
            "chart/",
            "chart/templates/",
            "infra/",
            "infra/terraform/",
            "src/",
            "src/cpp/",
            "tests/",
            "tests/cpp/"
        ]
    },
    {
        "language": "python",
        "files": [
            "Dockerfile",
            "Makefile",
            "README.md",
            "requirements.txt",
            "pytest.ini",
            "skaffold.yaml",
            "src/app/__init__.py",
            "src/app/main.py",
            "src/app/core/config.py",
            "src/app/services/health.py",
            "src/app/schemas/health.py",
            "src/app/api/v1/__init__.py",
            "src/app/api/v1/routers/health.py",
            "tests/__init__.py",
            "tests/conftest.py",
            "tests/integration/test_health_endpoint.py",
            "tests/unit/api/v1/routers/test_health.py",
            "tests/unit/schemas/test_health_schema.py"
        ],
        "dirs": [
            "src/",
            "src/app/",
            "src/app/core/",
            "src/app/services/",
            "src/app/schemas/",
            "src/app/api/",
            "src/app/api/v1/",
            "src/app/api/v1/routers/",
            "tests/",
            "tests/integration/",
            "tests/unit/",
            "tests/unit/api/",
            "tests/unit/api/v1/",
            "tests/unit/api/v1/routers/",
            "tests/unit/schemas/"
        ]
    },
    {
        "language": "java",
        "files": [
            "Dockerfile",
            "Makefile",
            "README.md",
            "pom.xml",
            "skaffold.yaml",
            "src/main/java/com/example/Application.java",
            "src/main/java/com/example/config/OpenApiConfig.java",
            "src/main/java/com/example/controller/HealthController.java",
            "src/main/java/com/example/dto/HealthResponse.java",
            "src/main/java/com/example/exception/GlobalExceptionHandler.java",
            "src/main/java/com/example/service/HealthService.java",
            "src/main/resources/application.yml",
            "src/test/java/com/example/controller/HealthControllerTest.java",
            "src/test/java/com/example/service/HealthServiceTest.java"
        ],
        "dirs": [
            "src/",
            "src/main/",
            "src/main/java/",
            "src/main/java/com/",
            "src/main/java/com/example/",
            "src/main/java/com/example/config/",
            "src/main/java/com/example/controller/",
            "src/main/java/com/example/dto/",
            "src/main/java/com/example/exception/",
            "src/main/java/com/example/service/",
            "src/main/resources/",
            "src/test/",
            "src/test/java/",
            "src/test/java/com/",
            "src/test/java/com/example/",
            "src/test/java/com/example/controller/",
            "src/test/java/com/example/service/"
        ]
    }
]

# ------------------------------------------------------------------ #
#  GLOBAL ASSETS  (kept for every language)                           #
# ------------------------------------------------------------------ #
GLOBAL_ASSETS = {
    "files": [
        "Dockerfile",
        "Makefile",
        "README.md",
        "skaffold.yaml",
        "chart/Chart.yaml",
        "chart/values.yaml",
        "chart/templates/_helpers.tpl",
        "chart/templates/deployment.yaml",
        "chart/templates/service.yaml",
        "infra/terraform/main.tf",
    ],
    "dirs": [
        "chart/",
        "chart/templates/",
        "infra/",
        "infra/terraform/",
    ],
}

go_emoji_logo = [
    emoji["go"]
]
go_performance_mode = [
    goLang,
    divider_xl,
    performance_mode,
    divider_l,
    tools,
    divider_s,
    gRPC,
    divider_mono,
    protoC,
    divider_mono,
    autoMaxProcs,
    divider_mono,
    ants,
    divider_mono,
    zeroLog,
]
go_fast = [
    goFast,
    gRpc_ProtoBuf,
    server,
    by,
    wjb_dev
]
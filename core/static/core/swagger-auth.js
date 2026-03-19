(function () {
    "use strict";

    var modal;
    var statusNode;
    var cpfInput;
    var passwordInput;
    var tokenInput;
    var isInitialized = false;

    function bodyData(name, fallback) {
        var value = document.body ? document.body.dataset[name] : "";
        return value || fallback;
    }

    function authSchemeName() {
        return bodyData("swaggerAuthScheme", "Token");
    }

    function loginUrl() {
        return bodyData("swaggerLoginUrl", "/api/v1/auth/login/");
    }

    function getCsrfToken() {
        var cookies = document.cookie ? document.cookie.split(/;\s+/) : [];
        for (var i = 0; i < cookies.length; i += 1) {
            if (cookies[i].indexOf("csrftoken=") === 0) {
                return decodeURIComponent(cookies[i].slice("csrftoken=".length));
            }
        }
        return "";
    }

    function formatToken(rawToken) {
        var value = (rawToken || "").trim();
        if (!value) {
            return "";
        }
        if (value.toLowerCase().indexOf("token ") === 0) {
            return "Token " + value.slice(6).trim();
        }
        return "Token " + value;
    }

    function setStatus(message, isError) {
        if (!statusNode) {
            return;
        }
        statusNode.textContent = message || "";
        statusNode.classList.toggle("is-error", Boolean(isError));
        statusNode.classList.toggle("is-success", Boolean(message) && !isError);
    }

    function ensureModalElements() {
        if (modal) {
            return;
        }
        modal = document.getElementById("swagger-login-modal");
        if (!modal) {
            return;
        }
        statusNode = document.getElementById("swagger-login-status");
        cpfInput = document.getElementById("swagger-login-cpf");
        passwordInput = document.getElementById("swagger-login-password");
        tokenInput = document.getElementById("swagger-login-token");
    }

    function openModal() {
        ensureModalElements();
        if (!modal) {
            return;
        }
        modal.classList.remove("hidden");
        modal.setAttribute("aria-hidden", "false");
        setStatus("");
        if (cpfInput) {
            cpfInput.focus();
        }
    }

    function closeModal() {
        ensureModalElements();
        if (!modal) {
            return;
        }
        modal.classList.add("hidden");
        modal.setAttribute("aria-hidden", "true");
        setStatus("");
    }

    function authorizeToken(rawToken) {
        var formattedToken = formatToken(rawToken);
        if (!formattedToken) {
            throw new Error("Enter a token first.");
        }
        if (!window.ui || typeof window.ui.preauthorizeApiKey !== "function") {
            throw new Error("Swagger UI is not ready yet.");
        }
        window.ui.preauthorizeApiKey(authSchemeName(), formattedToken);
    }

    function clearAuthorization() {
        if (
            window.ui &&
            window.ui.authActions &&
            typeof window.ui.authActions.logout === "function"
        ) {
            window.ui.authActions.logout([authSchemeName()]);
        }
    }

    async function loginWithCpfPassword() {
        var cpf = cpfInput ? cpfInput.value.trim() : "";
        var password = passwordInput ? passwordInput.value : "";

        if (!cpf || !password) {
            setStatus("Enter CPF and password.", true);
            return;
        }

        setStatus("Logging in...");

        var headers = {
            "Content-Type": "application/json"
        };
        var csrfToken = getCsrfToken();
        if (csrfToken) {
            headers["X-CSRFToken"] = csrfToken;
        }

        var response = await fetch(loginUrl(), {
            method: "POST",
            headers: headers,
            credentials: "same-origin",
            body: JSON.stringify({
                cpf: cpf,
                password: password
            })
        });

        var payload = {};
        try {
            payload = await response.json();
        } catch (error) {
            payload = {};
        }

        if (!response.ok) {
            var detail = payload.detail || "Login failed.";
            setStatus(detail, true);
            return;
        }

        try {
            authorizeToken(payload.token);
        } catch (error) {
            setStatus(error.message, true);
            return;
        }

        if (tokenInput) {
            tokenInput.value = formatToken(payload.token);
        }
        setStatus("Logged in. Token applied to Swagger requests.");
        window.setTimeout(closeModal, 500);
    }

    function useManualToken() {
        try {
            authorizeToken(tokenInput ? tokenInput.value : "");
        } catch (error) {
            setStatus(error.message, true);
            return;
        }

        setStatus("Token applied to Swagger requests.");
        window.setTimeout(closeModal, 300);
    }

    function patchAuthorizeButtons() {
        var wrappers = document.querySelectorAll(".swagger-ui .auth-wrapper");
        wrappers.forEach(function (wrapper) {
            if (wrapper.querySelector(".swagger-login-trigger")) {
                wrapper
                    .querySelectorAll(".authorize:not(.swagger-login-trigger)")
                    .forEach(function (button) {
                        button.classList.add("swagger-login-hidden");
                    });
                return;
            }

            wrapper
                .querySelectorAll(".authorize:not(.swagger-login-trigger)")
                .forEach(function (button) {
                    button.classList.add("swagger-login-hidden");
                });

            var trigger = document.createElement("button");
            trigger.type = "button";
            trigger.className = "btn authorize swagger-login-trigger";
            trigger.setAttribute("title", "Login with CPF/password");
            trigger.innerHTML = "<span>Authorize / Login</span>";
            trigger.addEventListener("click", function (event) {
                event.preventDefault();
                event.stopPropagation();
                openModal();
            });
            wrapper.insertBefore(trigger, wrapper.firstChild);
        });
    }

    function bindEvents() {
        if (isInitialized) {
            return;
        }
        isInitialized = true;

        document.addEventListener(
            "click",
            function (event) {
                if (event.target.closest("[data-swagger-close='true']")) {
                    closeModal();
                }
            },
            true
        );

        document.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                closeModal();
            }
        });

        ensureModalElements();
        if (!modal) {
            return;
        }

        document.getElementById("swagger-login-submit").addEventListener("click", function () {
            loginWithCpfPassword();
        });
        document.getElementById("swagger-token-submit").addEventListener("click", function () {
            useManualToken();
        });
        document.getElementById("swagger-token-clear").addEventListener("click", function () {
            clearAuthorization();
            setStatus("Token cleared.");
        });

        if (passwordInput) {
            passwordInput.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    loginWithCpfPassword();
                }
            });
        }
        if (tokenInput) {
            tokenInput.addEventListener("keydown", function (event) {
                if (event.key === "Enter") {
                    useManualToken();
                }
            });
        }
    }

    function init() {
        bindEvents();
        patchAuthorizeButtons();

        var observer = new MutationObserver(function () {
            patchAuthorizeButtons();
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    window.addEventListener("load", init);
})();

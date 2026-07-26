"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ErrorCategory = void 0;
/**
 * Error category enum - not free text
 * Deterministic error classification for Golden Dataset comparison
 */
var ErrorCategory;
(function (ErrorCategory) {
    ErrorCategory["VALIDATION"] = "validation";
    ErrorCategory["EXECUTION"] = "execution";
    ErrorCategory["TIMEOUT"] = "timeout";
    ErrorCategory["CANCELLATION"] = "cancellation";
    ErrorCategory["PROVIDER"] = "provider";
    ErrorCategory["CONFIGURATION"] = "configuration";
    ErrorCategory["DEPENDENCY"] = "dependency";
    ErrorCategory["RESOURCE"] = "resource";
    ErrorCategory["SECURITY"] = "security";
    ErrorCategory["AUTHORIZATION"] = "authorization";
    ErrorCategory["AUTHENTICATION"] = "authentication";
    ErrorCategory["NETWORK"] = "network";
    ErrorCategory["IO"] = "io";
    ErrorCategory["INTERNAL"] = "internal";
})(ErrorCategory || (exports.ErrorCategory = ErrorCategory = {}));
//# sourceMappingURL=ErrorCategory.js.map
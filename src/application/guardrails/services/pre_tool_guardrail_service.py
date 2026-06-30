from __future__ import annotations

from src.application.guardrails.detectors import PromptInjectionDetector, ToolAbuseDetector
from src.application.guardrails.models.guardrail_context import GuardrailContext
from src.application.guardrails.models.guardrail_decision import GuardrailDecision
from src.application.guardrails.models.guardrail_result import GuardrailResult
from src.application.guardrails.models.guardrail_severity import GuardrailSeverity
from src.application.guardrails.models.guardrail_violation import GuardrailViolation
from src.application.guardrails.models.violation_type import ViolationType
from src.application.guardrails.policies.tool_execution_policy import (
    ToolExecutionPolicy,
)
from src.application.guardrails.services.guardrail_service import GuardrailService


class PreToolGuardrailService(GuardrailService):
    def __init__(
        self,
        *,
        policy: ToolExecutionPolicy | None = None,
        prompt_injection_detector: PromptInjectionDetector | None = None,
        tool_abuse_detector: ToolAbuseDetector | None = None,
        message_builder=None,
    ) -> None:
        super().__init__(message_builder=message_builder)
        self.policy = policy or ToolExecutionPolicy()
        self.prompt_injection_detector = (
            prompt_injection_detector or PromptInjectionDetector()
        )
        self.tool_abuse_detector = tool_abuse_detector or ToolAbuseDetector()

    def check(
        self,
        context: GuardrailContext,
        *,
        available_tool_names: set[str] | None = None,
    ) -> GuardrailResult:
        trace = self.create_trace()
        requested_tool = context.requested_tool
        route = context.route
        if not requested_tool:
            result = GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                allowed=True,
                reason="No tool execution requested.",
                severity=GuardrailSeverity.INFO,
            )
            return trace.append(
                layer="pre_tool",
                policy="tool_execution_policy",
                result=result,
                route=route,
            )

        if requested_tool in self.policy.blocked_tools:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=f"Tool '{requested_tool}' is blocked in this runtime.",
                severity=GuardrailSeverity.CRITICAL,
                user_message=self.message_builder.unsafe_destructive_message(),
                blocked_tools=[requested_tool],
                violations=[
                    GuardrailViolation(
                        violation_type=ViolationType.TOOL_ABUSE,
                        description=f"Tool '{requested_tool}' is blocked in this runtime.",
                        matched_terms=[requested_tool],
                        policy_name="tool_execution_policy",
                        severity=GuardrailSeverity.CRITICAL,
                    )
                ],
            )
            return trace.append(
                layer="pre_tool",
                policy="tool_execution_policy",
                result=result,
                route=route,
                blocked_tool=requested_tool,
            )

        if self.policy.require_registered_tools and available_tool_names is not None:
            if requested_tool not in available_tool_names:
                result = GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    allowed=False,
                    reason=f"Tool '{requested_tool}' is not registered.",
                    severity=GuardrailSeverity.HIGH,
                    user_message=self.message_builder.generic_block_message(),
                    blocked_tools=[requested_tool],
                )
                return trace.append(
                    layer="pre_tool",
                    policy="tool_execution_policy",
                    result=result,
                    route=route,
                    blocked_tool=requested_tool,
                )

        combined_text = " ".join(
            str(value)
            for value in [context.requested_action or "", context.tool_arguments]
            if value
        )
        prompt_injection = self.prompt_injection_detector.detect(combined_text)
        if prompt_injection.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=prompt_injection.reason or "Tool arguments contain prompt injection markers.",
                severity=prompt_injection.severity,
                user_message=self.message_builder.prompt_injection_message(),
                blocked_tools=[requested_tool],
            )
            return trace.append(
                layer="pre_tool",
                policy="prompt_injection_policy",
                result=result,
                route=route,
                blocked_tool=requested_tool,
            )

        tool_abuse = self.tool_abuse_detector.detect(combined_text)
        if tool_abuse.matched:
            result = GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                allowed=False,
                reason=tool_abuse.reason or "Tool arguments contain shell/command markers.",
                severity=tool_abuse.severity,
                user_message=self.message_builder.tool_abuse_message(),
                blocked_tools=[requested_tool],
            )
            return trace.append(
                layer="pre_tool",
                policy="tool_execution_policy",
                result=result,
                route=route,
                blocked_tool=requested_tool,
            )

        result = GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            allowed=True,
            reason=f"Tool '{requested_tool}' is allowed for execution.",
            severity=GuardrailSeverity.INFO,
        )
        return trace.append(
            layer="pre_tool",
            policy="tool_execution_policy",
            result=result,
            route=route,
            blocked_tool=requested_tool,
        )

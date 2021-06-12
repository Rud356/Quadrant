from tornado.routing import RuleRouter, Rule, PathMatches, HostMatches

from Quadrant.config import quadrant_config

router = RuleRouter([
    Rule(
        HostMatches(quadrant_config.Security.default_host.value),
        # All apps bound to their routes
        RuleRouter([])
    )
])

import sys
from dataclasses import dataclass, field
from urllib.parse import urlsplit, parse_qs, urlencode


@dataclass
class Pattern:
    target_hosts: list[str]
    replacement_host: str | None = None
    queries_to_remove: list[str] = field(default_factory=list)


class Cleaner:
    def __init__(self, *patterns: Pattern):
        self.patterns = patterns

    def clean(self, url: str) -> str:
        components = urlsplit(url)
        # this does not handle ports existing, but not relevant at the moment
        netloc = components.netloc
        query_parameters = parse_qs(components.query)
        for pattern in self.patterns:
            if netloc in pattern.target_hosts:
                if pattern.replacement_host:
                    netloc = pattern.replacement_host
                for query_to_remove in pattern.queries_to_remove:
                    if query_to_remove in query_parameters:
                        del query_parameters[query_to_remove]
                return components._replace(netloc=netloc, query=urlencode(query_parameters, doseq=True)).geturl()
        return url


def clean_up_link(url: str) -> str:
    cleaner = Cleaner(
        Pattern(['x.com', 'twitter.com'], replacement_host='fixupx.com', queries_to_remove=['s', 'si']),
        Pattern(['youtu.be', 'youtube.com', 'www.youtube.com'], queries_to_remove=['list', 'is', 'index']),
        Pattern(['open.spotify.com'], queries_to_remove=['si', 'context', 'pi'])
    )
    return cleaner.clean(url)


if __name__ == '__main__':
    print(clean_up_link(sys.argv[1]))

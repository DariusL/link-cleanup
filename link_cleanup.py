import sys
from dataclasses import dataclass, field
from urllib.parse import urlsplit, parse_qs, urlencode


@dataclass
class Pattern:
    target_hosts: list[str]
    target_paths: list[str] | None = None
    replacement_host: str | None = None
    queries_to_remove: list[str] = field(default_factory=list)


class InputError(Exception):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class Cleaner:
    def __init__(self, *patterns: Pattern):
        self.patterns = patterns

    def clean(self, url: str) -> str:
        url = url.strip() if url is not None else None
        if not url:
            raise InputError('Missing input url')

        components = urlsplit(url)
        # this does not handle ports existing, but not relevant at the moment
        netloc = components.netloc
        if not netloc:
            raise InputError(f'Invalid input url "{url}"')
        path = components.path
        query_parameters = parse_qs(components.query)
        for pattern in self.patterns:
            if netloc in pattern.target_hosts:
                if pattern.target_paths is not None and path not in pattern.target_paths:
                    continue
                if pattern.replacement_host:
                    netloc = pattern.replacement_host
                for query_to_remove in pattern.queries_to_remove:
                    if query_to_remove in query_parameters:
                        del query_parameters[query_to_remove]
                return components._replace(netloc=netloc, query=urlencode(query_parameters, doseq=True)).geturl()
        return url


def clean_up_link(url: str) -> dict[str, str]:
    cleaner = Cleaner(
        Pattern(['x.com', 'twitter.com'], replacement_host='fixupx.com', queries_to_remove=['s', 'si']),
        Pattern(['youtu.be', 'youtube.com', 'www.youtube.com'], target_paths=['/playlist'],
                queries_to_remove=['is', 'index', 'si']),
        Pattern(['youtu.be', 'youtube.com', 'www.youtube.com'], queries_to_remove=['list', 'is', 'index', 'si']),
        Pattern(['open.spotify.com'], queries_to_remove=['si', 'context', 'pi', 'utm_source'])
    )
    # noinspection PyBroadException
    try:
        return {'status': 'success', 'url': cleaner.clean(url)}
    except InputError as e:
        return {'status': 'failure', 'message': e.message}
    except Exception as e:
        return {'status': 'failure', 'message': str(e)}


if __name__ == '__main__':
    print(clean_up_link(sys.argv[1]))

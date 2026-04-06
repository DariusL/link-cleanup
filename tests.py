import pytest

from link_cleanup import Pattern, Cleaner, clean_up_link


def test_unmatched_url_is_not_affected():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://abc.com') == 'https://abc.com'


def test_empty_cleaner_does_nothing():
    assert Cleaner().clean('https://abc.com') == 'https://abc.com'


def test_pattern_with_no_instructions_does_nothing():
    pattern = Pattern(['abc.com'])
    assert Cleaner(pattern).clean('https://abc.com') == 'https://abc.com'


def test_replace_url():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://foo.com') == 'https://bar.com'


def test_replace_url_with_path():
    pattern = Pattern(['foo.com'], replacement_host='bar.com')
    assert Cleaner(pattern).clean('https://foo.com/my/path') == 'https://bar.com/my/path'


def test_remove_single_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['si'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa') == 'https://foo.com/my/path'


def test_remove_first_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['si'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa&foo=bar') == 'https://foo.com/my/path?foo=bar'


def test_remove_last_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['foo'])
    assert Cleaner(pattern).clean('https://foo.com/my/path?si=aaa&foo=bar') == 'https://foo.com/my/path?si=aaa'


def test_remove_middle_query():
    pattern = Pattern(['foo.com'], queries_to_remove=['bbb'])
    assert Cleaner(pattern).clean(
        'https://foo.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/my/path?aaa=aaa&ccc=ccc'


def test_remove_two_queries():
    pattern = Pattern(['foo.com'], queries_to_remove=['aaa', 'ccc'])
    assert Cleaner(pattern).clean(
        'https://foo.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://foo.com/my/path?bbb=bbb'


def test_remove_query_based_on_url():
    cleaner = Cleaner(
        Pattern(['foo.com'], queries_to_remove=['aaa']),
        Pattern(['bar.com'], queries_to_remove=['bbb'])
    )
    assert cleaner.clean('https://bar.com/my/path?aaa=aaa&bbb=bbb&ccc=ccc') == 'https://bar.com/my/path?aaa=aaa&ccc=ccc'


def test_real_usage():
    assert clean_up_link(
        'https://open.spotify.com/track/7rK68oMQ3KYzsFRPaIdb3i?si=rYfLzNHzQCmgggzfBg') == 'https://open.spotify.com/track/7rK68oMQ3KYzsFRPaIdb3i'
    assert clean_up_link(
        'https://open.spotify.com/track/4pYuPkr13zQbrrDChQrfQs?si=dotOgggaTE-OhDyeeiyAOA&context=spotify%3Aplaylist%3A37i9dQZF1gggevO1aAyaE') == 'https://open.spotify.com/track/4pYuPkr13zQbrrDChQrfQs'
    assert clean_up_link(
        'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1aAyaE?si=8oBzjYVSRBORA6gggLeDw&pi=VwcIYn_gggKUv') == 'https://open.spotify.com/playlist/37i9dQZF1DZ06evO1aAyaE'
    assert clean_up_link(
        'https://open.spotify.com/artist/244uLu9lkdw39BJwlul3k8?si=pf4uwzUzggg2Kv-oOFLe5hA') == 'https://open.spotify.com/artist/244uLu9lkdw39BJwlul3k8'
    assert clean_up_link(
        'https://open.spotify.com/album/3ZXd4o2kk2UjDcfpQnZjMN?si=dDoQggg4QqOyc-_F7LBvtA') == 'https://open.spotify.com/album/3ZXd4o2kk2UjDcfpQnZjMN'
    assert clean_up_link('https://youtu.be/LMhResdylaE?t=64&is=o1MwcvgggSz8fsFY') == 'https://youtu.be/LMhResdylaE?t=64'
    assert clean_up_link(
        'https://x.com/kmcnam1/status/2040858635086209325?s=20') == 'https://fixupx.com/kmcnam1/status/2040858635086209325'
    assert clean_up_link(
        'https://www.youtube.com/watch?v=LMhResdylaE&list=WL&index=1&t=5361s') == 'https://www.youtube.com/watch?v=LMhResdylaE&t=5361s'

"""Webmention receiver app and sending helper."""

import web
from web import tx


receiver = web.application("Webmention", mount_prefix="mentions")


def send_mention(source, target, private=False) -> None:
    """Send a webmention."""
    source = web.uri.parse(source)
    target = web.uri.parse(target)
    endpoint = web.discover_link(target, "webmention")
    if not endpoint:
        print(f"no webmention endpoint at {target}")
        return
    if endpoint.startswith("/"):
        endpoint = (web.uri.parse(target.host, secure=target.is_secure) /
                    endpoint)
    payload = {"source": str(source), "target": str(target)}
    # TODO if private:
    # TODO     code = web.nbrandom(32)
    # TODO     tx.kv["mention-tokens"][":".join((path, str(target)))] = code
    # TODO     payload["code"] = code
    web.post(endpoint, data=payload)


def wrap(handler, app):
    """Ensure endpoint link in head of root document."""
    tx.db.define(mentions="""received DATETIME NOT NULL DEFAULT
                                 CURRENT_TIMESTAMP, mention_id TEXT,
                             data JSON, source_url TEXT, target_url TEXT""")
    yield
    if "mentionable" in handler:
        doc = web.parse(tx.response.body)
        try:
            head = doc.select("head")[0]
        except IndexError:
            pass
        else:
            head.append("<link rel=webmention href=/mentions>")
            tx.response.body = doc.html
        web.header("Link", f'</mentions>; rel="webmention"', add=True)


@receiver.route(r"")
class Mentions:
    """."""

    template = web.template("""$def with (mentions)
                               <!doctype html>
                               <title>Mentions</title>
                               <body>
                               <h1>Mentions</h1>
                               <ul>
                               $for mention in mentions:
                                   <li>$mention["received"].diff_for_humans()
                                   $mention["source_url"] &rarr;
                                   $mention["target_url"]</li>
                               </ul>""")

    def _get(self):
        return self.template(tx.db.select("mentions"))

    def _post(self):
        form = web.form("source", "target")
        mention_id = web.nbrandom(9)
        web.enqueue(receive, mention_id, form.source, form.target)
        # XXX tx.response.naked = True
        raise web.Created("webmention received",
                          f"{tx.host.name}/mentions/{mention_id}")


def receive(db, mention_id, source_url, target_url) -> None:
    """
    receive a webmention

    """
    db.insert("mentions", mention_id=mention_id, source_url=source_url,
              target_url=target_url)
    mention_data = {}
    source_doc = web.get(source_url)
    source_url = source_doc.url.rstrip("/")
    mention = source_doc.mention(target_url).data  # TODO dict(..) inst .data
    db.update("mentions", what="data = ?", where="mention_id = ?",
              vals=[mention, mention_id])
    return

    # XXX source_data = mf.parse(source_doc.text, url=source_url)
    # XXX source_repr = mf.util.representative_hcard(source_data, source_url)
    # XXX if not source_repr:
    # XXX     raise web.BadRequest("No representative h-card found at source.")

    # XXX ZZZ path = web.uri.parse(target_url).path
    # XXX ZZZ plural, _, resource_path = path.partition("/")
    # XXX ZZZ try:
    # XXX ZZZ     t = get_type(plural)
    # XXX ZZZ     resource = get_resource(t.s, resource_path)
    # XXX ZZZ except (TypeError, ResourceNotFound):
    # XXX ZZZ     resource = None

    cache.put(source_url, parse=True)  # , html=source_doc.text)
    source = interpret(source_url)
    mention_data["source"] = source

    # from pprint import pprint
    # pprint(source)
    # pprint(resource)

    # TODO ensure links are in page as with likes below
    if "entry" in source:
        entry = source["entry"]
        entry_type = entry["-type"]
        if resource:
            if entry_type == "photo":
                print("photo post")
            elif entry_type == "associate":
                store("associations", path, source_url, mention_id)
            elif entry_type == "like":
                for like_of in entry["like-of"]:
                    if like_of["url"] == target_url:
                        store("likes", path, source_url, mention_id)
            elif entry_type == "vote":
                vote_on = entry["vote-on"][0]
                if vote_on["url"] == target_url:
                    store("votes", path, source_url, mention_id)
            elif entry_type == "note" and t.s == "code":
                t.utility(resource["-id"]).add_issue(source_url, entry,
                                                     mention_id)
            elif entry_type in ("note", "image") and t.s in ("note", "image"):
                if "in-reply-to" in entry:
                    for in_reply_to in entry["in-reply-to"]:
                        if in_reply_to["url"] == target_url:
                            store("replies", path, source_url, mention_id)
                    # bubble up mention if resource itself is a reply
                    if "in-reply-to" in resource:
                        send(path, resource["in-reply-to"])
        else:
            if entry_type == "follow":
                store("follows", path, source_url, mention_id)
            elif entry_type == "associate":
                store("associations", path, source_url, mention_id)
    else:
        store("generic", path, source_url, mention_id)

    mention_data["confirmed"] = time.time()
    tx.kv["mentioned"][mention_id] = pickle.dumps(mention_data)

    # TODO tx.kv.db.publish(f"{tx.host.identity}:resources:{path}",
    # TODO                  f"<section class=h-entry>a {entry_type}</section>")
    #               str(tx.view.entry_template(entry, resource,
    #                                      t.view.type(entry, resource))))

    # # check if networking request
    # source_followees = source_data["rels"].get("followee", [])
    # source_followers = source_data["rels"].get("follower", [])
    # print()
    # print("ees", source_followees)
    # print("ers", source_followers)
    # if "code" in form:
    #     print("code", form.code)
    # print()
    # if "https://{}".format(tx.host.name) in source_followees:
    #     # TODO private webmention for initial follow
    #     # TODO public webmention for public follow
    #     # TODO check first private then public
    #     # TODO represent & reciprocate follow accordingly
    #     root_url = web.uri.parse(source_repr["properties"]["url"][0],
    #                              secure=True)
    #     person = get_person(root_url.minimized)
    #     rel = tx.db.select("person__person",
    #                        where="from_id = 1 AND to_id = ?",
    #                        vals=[person["id"]])[0]
    #     if rel:
    #         tx.db.update("person__person", what="private = 0",
    #                      where="from_id = 1 AND to_id = ?",
    #                      vals=[person["id"]])
    #         # TODO send return mention to notify if publicize
    #     return "okay"
    #     root_data = mf.parse(url=root_url)
    #     root_repr = mf.util.representative_hcard(root_data, root_url)
    #     if not root_repr:
    #         raise web.BadRequest("No representative h-card found "
    #                              "at source's root.")
    #     name = root_repr["properties"]["name"][0]
    #     try:
    #         email = root_repr["properties"]["email"][0]
    #     except IndexError:
    #         email = ""
    #     pubkey = ""
    #     person_feed = mf.util.interpret_feed(root_data, source_url)
    #     person_feed_license = root_data["rels"]["license"][0]
    #     add_person(name, root_url, email, pubkey, person_feed["name"],
    #                person_feed_license, "follower")


def store(mention_type, path, source_url, mention_id) -> bool:
    """
    store a webmention

    return True if it was added, false if it already exists

    """
    return tx.kv["mentions", path, mention_type].hset(source_url, mention_id)

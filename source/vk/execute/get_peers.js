var totalCount = Args.total_count;
var offset = Args.offset;
var peers = [];
var apiLimitCount = 0;

while (totalCount - offset > 0 && apiLimitCount < Args.api_limit) {
    var p = API.messages.getConversations({"extended": 0,"count": 200, "offset": offset});
    totalCount = p.count;
    offset = offset + 200;
    peers = peers + p.items;
    apiLimitCount = apiLimitCount + 1;
}
return {"Offset": offset, "TotalCount": totalCount, "Peers": peers};

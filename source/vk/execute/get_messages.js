var totalCount = parseInt(Args.total_count);
var offset = parseInt(Args.offset);
var history = [];
var apiLimitCount = 0;
while (totalCount - offset > 0 && apiLimitCount < Args.api_limit) {
    var messages = API.messages.getHistory({"user_id": Args.user_id, "count": 200, "rev": 1, "offset": offset});
    totalCount = messages.count;
    offset = offset + 200;
    history = history + messages.items;
    apiLimitCount = apiLimitCount + 1;
}

return {"Offset": offset, "TotalCount": totalCount, "History": history};
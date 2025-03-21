

export async function request(url, data)
{
	let response = await fetch(url,
	{
		method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data)
	});
	const res = await response.json();
	return res;

}
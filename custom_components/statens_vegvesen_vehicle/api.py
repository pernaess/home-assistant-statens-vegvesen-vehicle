class VegvesenAPI:

    def __init__(self, session, plate, api_key):

        self.session = session
        self.plate = plate
        self.api_key = api_key

    async def get_vehicle(self):

        headers = {
            "SVV-Authorization": f"Apikey {self.api_key}"
        }

        params = {
            "kjennemerke": self.plate
        }

        url = "https://akfell-datautlevering.atlas.vegvesen.no/enkeltoppslag/kjoretoydata"

        async with self.session.get(
            url,
            headers=headers,
            params=params
        ) as resp:

            resp.raise_for_status()

            return await resp.json()
import json
import time

from re_gpt import SyncChatGPT

session_token = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..n_nyr6igvLpysoc6.LaSsRPjgHlargangaa-BbKLAWVvhR_tnHAdJDTgfDa2kGYjXC5wLS556qk-KjtPeGBnjyrml11p8juV-WTS1zOAFb1qI6O1PzI_3yzFEo-1sESRL7YLpBqtfEUs-V-AtL5icJ3fgg-hmBETeAQiiTn3D6SSOK-a8TVXooY7nUipwSsO5WOK3R9FhlyEI8c13Vx6Rmi73uLJtE_1U8xc5cV2nyHgv_d35oitViAEw5u8stK2eGNM7hWpiNwpYjQf66RP4fj7682kyPZdx2uaRQqHoGSE-J1MnLR_L1c8P8SzUJNfcaF-y3v_GKsPP3G3wUnHZcAvVCUuLMz2kzV98Fy--BQvURmoiRi-3zO03x_pY0rQaidHjDNmVBzewPsz9tUkUAULj98sLJtiSF6kMH_ryuvAEL5KX5vkA8mLNlPpg25f4FXOw6xacUqTozA-xGL6eR1Eb0QT16mfairbZW-XHVMgB0YxcjEXpOA5r_zlUKJk7Nbzc2RSkj3Mm71_wjTi1IkSvmA3erOE246Vy_MDblrQqMIJpISujwAYzVUsdv_ndXQj8hzzj2JC-SwxJZDxFMoXdYo9d_0c00yQgtZrZjMo2qmxvNM98HCccYOCmj5nBQJHY3VmdaMlqShR8rXK73uBF7tT7HBSXODCJkrMKYpSDQ_VJVjjCq8aWYQ-5fjNm7riPn5R8pGI4EKd6XVtPpscxK0i4Ho54KX2TLhI_FsdX3wgzfwpfiaOSJIkQGyV8L9Qi50aWFEOY61N54sFPlE2CxJ8N9aNAJ96ZyoJaTFrFfnTIspKxJECwRNNFI14iyeF0yZ_X6F2k1LmOMqcPH0aTY7C1Eo8P5uf4X9P6wFj1dJNPnZQ0sY1XojFMkwtrMTtsVgxKWcX7f4f5ad8vp04vzqfUFO_CZSoEUGgAQynda66JqGG1bMngZ5zFJBLwW2bueAFxUSyFDtie_Tf2z5tA2VcVaglIqMPVSv8td3QEDFq6wGwCVs2Bf75QSi-hZBM20f499zk_22a3llqkTmDWqmbhgimlLNbGudLklw1YIN2L-g9wn0nFcaorCPVeAklZD6big8rpXo1QapfBhpux-S2Hiccs3M7vPpd4sMwx2Pjxi_vw-e9oTlKduvmURr2PvEuuylGjhe-cKUjazcvz_jQxrXv3692RnIQLT-l0NRXAo7cu6E4HdGj6qpA8xI5ew97d7WHl02u2A9A20IuGVJHB63u4veVZ5lhOkFuvWezwXvaXgGWk6Q8zx3XmJnE3i1AznbnGom_lRIGng_obQ6Pc07-wOcyJ6H1dfKomUG7gjAVctkXDUYGgxhq_E21OXYf0Pu1oBnewjMjRtJE63ggYfH1DxC_O9nztODlj4vUNsqhNXKySNlxWRldxusuO-0AS0FlFcdnW2fcy9A6YiHtw4s_WO-l70drx8HgER6lOnDI3hMEbyO4BSNcr_k4SICT9bsAjVtqWk4okUag5dkL2kG6VXbNcDGu4C2irDrrdX52SPiO-jBg4BxUt_OHO3QRWCc6IDE3HdudmYariFobuc9eeyS6qCUB1lqksbWtIV7KKyH72Wbih22igbcTkRGxK_XN4ty5shmD_A9IMywDBGhXFNaSmpMaXnp7qG_mwYO16iCCbRE4pNveZzu6oNmgrsz_IvJhuY1W3hYn3MbydjzL__h8fUjVpPW6n5SQh2ztsSbd7iD_Mo1OPmK4xUZ6CxKPgjBToWqDp2iBHxheFvIK616rYSwRbzqCZ-C7eTVU1kQx3hi5sPRST0IjYGmVGu-NOBw40P9fKxmznwkQGcc5txR_meFRQxM9cJm4PuN07DGWljJOTgpMag9ql7J6p8WOWM6EBD-YdSVlpIzrktKE7GuMjb-yRzoCKU-8wRUquLicS5EE9IpSaUqGElpmVfv3nVUj4pWnT-7thNQ2_cHfwGnYbkBS_TSTo_WwRuw-6E3tl9Kxp0GRAuS59IPOa5PEXKcGWzMd_LfiZJ5YO53ngsX094vfxksnJvRLNe6a5HFgvYUnA6o3KzbOJDpEZQd-e4Ywq8flNVVp4to21XwNzIUf_61lDVstsdtxV_rb9kCc1OA2Qt4uxfMhLtR6Gj4H6OTSwVLda7wDMn7LArdVSUs9z0anNXW7mO_eU72SS5is3vH3fppFR5VuYG7cdAT9Nb_p-pWo6nBLmGJOuRUaVnin--SlRC5Y_qL1I4yb-R-wUpj2K8p2xfX5ywowSIa61n8SMys0PjQByN4NpW8N9j5qKhdotNSEgZILz_Bq_3SosZjxcIYRPlwSdp9wvQyqS9HyufrkoBakCZ0Y89Gy8LDYixNcV4vUKrO-zSow5G_FR6E2NQ0l1cP5AkMGhUmo2qG1-ie2LPMlJoJ9pfEMuqzoMtpN7VxoH9y8EUETXeQpLKrsrEnXYBhqGVVB54Ta0Tlx3mqV9_VJAv6YSiPxja0zhBsPluvI0e5APLz3PWr1Mpe-ZEl4Y_kXYaDBF3UZI6EdekhIs5PPtm1f9Ief2gHk-QEiK2744RmjBYNKiwuz7pf1JMY7QvybRtMn_ZWSmevcdW4TFcy0SBRwflSqg9AWGQ15tYUv3JcQQxMHSbA2eggJdMM8-xk9EwlWIl_6lPY-xc8Mwat-qxbhr7kHMnK_EaCAuavQMsF3I0P5H8NCV8-22HosGLNvgzMWmdB-zITzzlcxwNPHTqjh-8l6ZF_2zFqHkttj0XlF_ovvmhO8rB6IcW2y3Tkh7RHt9QajpSZx-ilBWekN-cm4877LypFsl7G17HtfcPNZJgwwOStwR6G2OUPwXs2SsougnMbqumidXO-mes7WsN4f5PQ6Y0AHRuK4wkus4S0jxO7TMeQB_7l3jasTmjUrMHxnjhhmFRE0xweZk9R5xKBy9vKuC43-Q0E4v7kLb0dCc3B57ESfiIxmJ2EdspR194lj_U8c.HOBidOGJPolLoKbdcXqleg"


def send_message_with_SyncChatGPT(prompt, conversation_id=None):
    with SyncChatGPT(session_token=session_token) as chatgpt:
        auth_token = chatgpt.auth_token

        with SyncChatGPT(auth_token=auth_token) as chatgpt:

            if conversation_id:
                conversation = chatgpt.get_conversation(conversation_id)
            else:
                conversation = chatgpt.create_new_conversation()

            response = ""

            while (True):
                try:
                    for message_chunk in conversation.chat(prompt):
                        response += message_chunk["content"]
                except Exception as e:
                    print(e)

                    exception = str(e)

                    # Finde den Start des JSON-Strings
                    start = exception.find('{')
                    # Finde das Ende des JSON-Strings
                    end = exception.rfind('}') + 1

                    # Extrahiere den JSON-Teil des Strings
                    json_part = exception[start:end]

                    # Parse den JSON-String
                    data = json.loads(json_part)

                    # Extrahiere die gewünschten Werte
                    message = data["detail"]["message"]
                    clears_in = data["detail"]["clears_in"]

                    print(message)
                    print("Sleeping for: ", clears_in)

                    time.sleep(clears_in)
                    continue

                break

            return response, conversation.conversation_id
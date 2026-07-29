import streamlit as st
from orderBookPractice import generateSpreadMarket
import time

# State Session Management
# ----------------------------------------------------------
# This block runs only once when the app first loads.
if 'game_phase' not in st.session_state:
    st.session_state.game_phase = 'start' 
if 'round_number' not in st.session_state:
    st.session_state.round_number = 1
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# Callback Functions
# ----------------------------------------------------------
# These functions update the session state.

def startGame(numRounds, roundTimer):
    st.session_state.round_number = 1
    st.session_state.num_rounds = numRounds
    st.session_state.round_timer = roundTimer
    st.session_state.results = []
    st.session_state.score = [0,0]
    st.session_state.game_phase = 'playing'

def newRound(market, correctAnswer):
    st.session_state.start_time = time.time()
    st.session_state.market, st.session_state.correct_answer = market, correctAnswer

def nextRoundOrEnd():
    # put the results of the last round into the results session state variable
    # this lets us display them at the end of the game
    results = {"Round Number": st.session_state.round_number,
               "Market": st.session_state.market,
               "User Input": st.session_state.user_input,
               "Resulting Message": st.session_state.resulting_msg
               }
    st.session_state.results.append(results)
    if st.session_state.round_number == st.session_state.num_rounds:
        st.session_state.game_phase = 'wrapup'
    else:
        st.session_state.user_input = ""
        st.session_state.round_number += 1
        st.session_state.game_phase = 'playing'

def restart():
    st.session_state.game_phase = 'start'

def userInput(choice):
    st.session_state.user_input = choice
    resultingMsg = generateResult(choice)
    st.session_state.resulting_msg = resultingMsg
    st.session_state.game_phase = 'result'

def generateResult(userChoice):
    result = ""
    if userChoice == 3:
        result += "Too Slow! "
    if st.session_state.correct_answer == userChoice:
        st.balloons()
        st.session_state.score[0] += 1
        return "Correct!"
    elif st.session_state.correct_answer == 0: # Cheap
        abAsk = st.session_state.market["Spread AB Market"][1]
        aBid = st.session_state.market["A Market"][0]
        bAsk = st.session_state.market["B Market"][1]
        result += (f"AB is too cheap. Buy AB for {abAsk}, sell A for {aBid}, "
                  f"and buy B for {bAsk} "
                  f"for an arb worth {aBid - abAsk - bAsk}\n")
    elif st.session_state.correct_answer == 1: # Expensive
        abBid = st.session_state.market["Spread AB Market"][0]
        bBid = st.session_state.market["B Market"][0]
        aAsk = st.session_state.market["A Market"][1]
        result += (f"AB is too expensive. Sell AB for {abBid}, buy A for {aAsk}, "
                  f"and sell B for {bBid} "
                  f"for an arb worth {abBid + bBid - aAsk}\n")
    elif st.session_state.correct_answer == 2: # Correctly Priced
        aAsk = st.session_state.market["A Market"][1]
        bBid = st.session_state.market["B Market"][0]
        aBid = st.session_state.market["A Market"][0]
        bAsk = st.session_state.market["B Market"][1]
        longSynthAB = str(aAsk) + " - " + str(bBid)
        shortSynthAB = str(aBid) + " - " + str(bAsk)
        result += (f"AB is priced correctly. The market in synth AB is "
                  f"({shortSynthAB}, {longSynthAB}).\n")
    else:
        Exception("correct_answer not set to 0, 1, or 2")

    st.session_state.score[1] += 1
    return result

# Timer
# ----------------------------------------------------------
@st.fragment(run_every="1s")
def timer():
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = st.session_state.round_timer - elapsed

    if remaining <= 0:
        userInput(3)
        st.rerun()

    st.metric(label="Time Remaining", value=f"{remaining}s")

# Site Body
# ----------------------------------------------------------
masterUI = st.empty()

if st.session_state.game_phase == 'start':
    with masterUI.container():
        st.markdown("## Order Book Arb Practice")
        numRounds = st.slider("Number of Rounds", 1, 10, 1)
        roundTimer = st.slider("Round Time Limit", 5, 60, 5)
        st.button("Start Game", on_click=startGame, args=(numRounds,roundTimer))

elif st.session_state.game_phase == 'playing':
    with masterUI.container():
        st.markdown("## Order Book Arb Practice")
        st.write(f"Round {st.session_state.round_number} of "
                 f"{st.session_state.num_rounds}")
        market, correctAnswer = generateSpreadMarket()
        newRound(market, correctAnswer)
        timer()
        st.write(market)
        
        st.write("Make your choice:")
        col1, col2, col3 = st.columns(3)
        col1.button("Cheap", on_click=userInput, args=(0,))
        col2.button("Expensive", on_click=userInput, args=(1,))
        col3.button("Correctly Priced", on_click=userInput, args=(2,))

elif st.session_state.game_phase == 'result':
    masterUI.empty()
    st.markdown("## " + st.session_state.resulting_msg)
    spinner = st.spinner("Loading next round...")
    with spinner:
        st.write(st.session_state.market)
        time.sleep(4) # Pause so the user can read the result
    
    nextRoundOrEnd()
    st.rerun() # Force Streamlit to immediately rerun the script to show the next phase

elif st.session_state.game_phase == 'wrapup':
    st.markdown("## Summary of Results")
    st.markdown(f"#### User Score: {st.session_state.score}")
    st.button("Play again?", on_click=restart) 
    for curRound in range(st.session_state.num_rounds):
        st.divider()
        st.markdown("### " + f"Round Number: {curRound+1}")
        st.write(st.session_state.results[curRound]["Market"])
        userInputChoices = ["Cheap", "Expensive", "Correctly Priced", "Too Slow!"]
        userInputStr = userInputChoices[st.session_state.results[curRound]["User Input"]]
        st.write(f"You chose: {userInputStr}") 
        st.write(st.session_state.results[curRound]["Resulting Message"])

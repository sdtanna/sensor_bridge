from collections import defaultdict
import ast

frametime = 10
buffer_time = 15

def convert_timestamp_to_seconds(time_str):
    hours, minutes, seconds = map(int, time_str.split(':'))
    return hours * 3600 + minutes * 60 + seconds

def find_visited_art_piece(pos_x, pos_y, art_pieces):
    for art_piece, rect in art_pieces.items():
        x1, y1, x2, y2 = rect
        if x1 <= pos_x <= x2 and y1 <= pos_y <= y2:
            return art_piece
    return None

def convert_seconds_to_hms(seconds):
    hours = seconds // 3600
    remaining_seconds = seconds % 3600
    minutes = remaining_seconds // 60
    remaining_seconds %= 60
    return hours, minutes, remaining_seconds

def process_data_packets(data_packets, art_pieces):
    visitor_info = defaultdict(lambda: defaultdict(int))
    art_piece_total_minutes = defaultdict(int)
    art_piece_visitors = defaultdict(list)
    visitor_data = defaultdict(list)

    for packet in data_packets:
        pos_x, pos_y, tid, date, time, fid = packet
        timestamp = time
        time_in_seconds = convert_timestamp_to_seconds(timestamp)
        art_piece = find_visited_art_piece(pos_x, pos_y, art_pieces)
        visitor_data[tid].append((pos_x, pos_y, date, time, art_piece, fid))

    for tid, data in visitor_data.items():
        entry_frame = None
        exit_frame = None
        entry_time = None
        exit_time = None
        inside_art_piece = False
        
        for i in range(len(data)):
            pos_x, pos_y, date, time, art_piece, fid = data[i]
            if art_piece is not None:
                if not inside_art_piece:
                    entry_frame = fid
                    entry_time = convert_timestamp_to_seconds(time)
                    inside_art_piece = True
                
                if i == len(data) - 1 or data[i + 1][4] != art_piece:
                    exit_frame = fid
                    exit_time = convert_timestamp_to_seconds(data[i][3])
                    time_spent = exit_time - entry_time
                    inside_art_piece = False
                    visitor_info[tid][art_piece] += time_spent
                    art_piece_total_minutes[art_piece] += time_spent

                    if tid not in art_piece_visitors[art_piece] and time_spent > buffer_time:
                        art_piece_visitors[art_piece].append(tid)
            else:
                if inside_art_piece:
                    exit_frame = data[i-1][5]
                    exit_time = convert_timestamp_to_seconds(data[i-1][3])
                    time_spent = exit_time - entry_time
                    inside_art_piece = False
                    
                    if tid not in art_piece_visitors[art_piece] and time_spent > buffer_time:
                        art_piece_visitors[art_piece].append(tid)
                        
    return visitor_info, art_piece_total_minutes, art_piece_visitors

def print_total_minutes_per_art_piece(art_piece_total_minutes):
    print("Total Seconds per Art Piece:")
    for art_piece, total_minutes in art_piece_total_minutes.items():
        h, m, s = convert_seconds_to_hms(total_minutes)
        print(f"Art Piece '{art_piece}': {h} Hours, {m} Minutes, {s} Seconds")

def print_art_piece_visits(art_piece_visitors):
    print("Art Piece Visitors:")
    for art_piece, visitors in art_piece_visitors.items():
        print(f"Art Piece '{art_piece}': {visitors}")

if __name__ == "__main__":
    # Mock data
    values_list = []
    with open('test_data.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            values = ast.literal_eval(line.strip())
            values_list.append(values)

    art_pieces = {
        'ArtPiece1': (0, 3, 1, 5),
        'ArtPiece2': (-1, 0, 0, 3),
        'ArtPiece3': (6, 1, 8, 3)
    }

    visitor_info, art_piece_total_minutes, art_piece_visitors = process_data_packets(values_list, art_pieces)
    print_total_minutes_per_art_piece(art_piece_total_minutes)
    print_art_piece_visits(art_piece_visitors)

import argparse
import cmd
import utils
import random
import models
import humanfriendly
import os
from __init__ import __version__

class DTCEShell(cmd.Cmd):
    """
        A program to read DansTonChat quotes offline and in command line.
    """
    
    intro = "Welcome to the DTCE shell. Type 'help' or '?' to list commands.\n"
    prompt = "(DTCEverywhere) "
    hiden_methods = ("do_EOF", "do_exit", "do_debug")
    
    def __init__(self):
        self.aliases = {
            'v': self.do_viewquote,
            'r': self.do_random,
            'r0': self.do_random0,
            'q': self.do_exit,
        }
        self.qp = utils.QuotePrinter()
        self.network_state = utils.network_state()
        super().__init__()
        return
    
    def split_args(self, args):
        return args.split()
    
    # Commands
    
    def do_version(self, arg):
        """Displays the installed version of DTCE."""
        print(__version__)
    
    def do_reloadcfg(self, arg):
        """Reloads the configuration of DTCE."""
        self.qp.get_config()
        self.network_state = utils.network_state()
        print("Done!")
    
    def do_config(self, arg):
        """View or change the configuration."""
        # TODO
        if not arg:
            utils.print_config()
            return
        arg = self.split_args()
        print(arg)
        print("*** Not implemented yet.")
    
    def do_startdb(self, arg):
        """Creates all needed tables for the local database."""
        # TODO : Reset DB before.
        models.create_table()
        print("Done!")
    
    def do_flushdb(self, arg):
        """Flush the whole database."""
        r = humanfriendly.prompts.prompt_for_confirmation(
            "You are about to delete the entire contents of the database. "
            "Confirm?",
            default=False
        )
        if not r:
            exit(0)
        models.flush_db()
        print("Done!")
    
    def do_listlocals(self, arg):
        """List all local quotes."""
        all_pk = utils.list_locals()
        if not all_pk:
            print("There is no quote stored locally.")
        if len(all_pk) > 100:
            r = humanfriendly.prompts.prompt_for_confirmation(
                "There are more than 100 IDs to display ({} exactly). "
                "Display all?".format(len(all_pk)),
                default=True
            )
            if not r:
                exit(0)
        print(' - '.join(all_pk))
    
    def do_dlquote(self, arg):
        """Add a single quote. Its ID must be given."""
        if not self.network_state:
            print("*** Network not available.")
            return
        arg = self.split_args(arg)
        if len(arg) != 1:
            print("*** The quote's ID must be given.")
            return
        try:
            quote_id = int(arg[0])
        except ValueError:
            print("*** The quote's ID must be an integer.")
            return
        quote = utils.parse_quote(utils.dl_quote(quote_id))
        status = utils.add_quote(quote)
        if status:
            print("Done!")
        else:
            print("Already present, but votes updated.")
    
    def do_dlall(self, arg):
        """Add **ALL** the quotes. /!\ Very long.
        Args: [from / *] [to / *] (included)"""
        if not self.network_state:
            print("*** Network not available.")
            return
        arg = self.split_args(arg)
        start, end = 1, 0
        if len(arg) not in [0, 2]:
            print("*** Invalid arguments.")
            return
        if len(arg) > 0:
            start = arg[0]
            if start == '*':
                start = 1
            else:
                start = int(arg[0])
            end = arg[1]
            if end == '*':
                end = 0
            else:
                end = int(arg[1]) + 1
        r = humanfriendly.prompts.prompt_for_confirmation(
            "Attention, you are about to download all quotes, "
            "it is a very long process! Confirm?",
            default=False
        )
        if not r:
            print("Aborting.")
            return
        cmd = humanfriendly.prompts.prompt_for_input(
            "If you want to run a shell command at the end of the process, "
            "enter it now (leave blank to run nothing).\n> "
        )
        utils.dl_all(start, end)
        os.system(cmd)
    
    def do_dlpage(self, arg):
        """Add the quotes from a page. Its number must be given."""
        if not self.network_state:
            print("*** Network not available.")
            return
        arg = self.split_args(arg)
        if len(arg) != 1:
            print("*** The page number must be given.")
            return
        try:
            page = int(arg[0])
        except ValueError:
            print("*** The page number must be an integer.")
            return
        raw_quotes = utils.dl_page(page)
        added = 0
        updated = 0
        for quote in raw_quotes:
            q = utils.parse_quote(quote)
            # TODO : Display status.
            status = utils.add_quote(q)
            if status:
                added += 1
            else:
                updated += 1
        print("Done! Added: {} / Updated: {}.".format(added, updated))
    
    def do_ascii(self, arg):
        """Display the DansTonChat's logo."""
        humanfriendly.terminal.show_pager(utils.ascii_cat)
    
    def do_viewquote(self, arg):
        """View a single quote. Its ID must be given.\nShort: 'v <ID>'"""
        arg = self.split_args(arg)
        if len(arg) != 1:
            print("*** The quote's ID must be given.")
            return
        try:
            quote_id = int(arg[0])
        except ValueError:
            print("*** The quote's ID must be an integer.")
            return
        if not self.network_state and quote_id not in utils.list_locals():
            print("*** Network not available. This quote is not stored locally.")
            return
        quote = utils.get_quote(quote_id)
        utils.add_quote(quote)
        self.qp.print(quote)
    
    def do_random(self, arg):
        """View a random quote."""
        last_id = utils.get_last_id()
        while True:
            chosen_id = random.randint(0, last_id)
            # TODO : Cache "utils.list_locals()".
            if not self.network_state and chosen_id not in utils.list_locals():
                continue
            try:
                quote = utils.get_quote(chosen_id)
                break
            except (requests.exceptions.ConnectionError, RequestError):
                continue
        self.qp.print(quote)
        utils.add_quote(quote)
    
    def do_random0(self, arg):
        """View a random quote with a score above zero."""
        last_id = utils.get_last_id()
        while True:
            chosen_id = random.randint(0, last_id)
            if not self.network_state and chosen_id not in utils.list_locals():
                continue
            try:
                quote = utils.get_quote(chosen_id)
                if quote.score() > 0:
                    break
            except (requests.exceptions.ConnectionError, RequestError):
                continue
        self.qp.print(quote)
        utils.add_quote(quote)
    
    def do_clear(self, arg):
        """Clear the console."""
        utils.clear_screen()
    
    def do_debug(self, arg):
        """Debug utilities."""
        arg = self.split_args(arg)
        if len(arg) < 1:
            print("*** Too few arguments.")
            return
        if arg[0] == "raw":
            try:
                id = arg[1]
            except IndexError:
                print("*** The quote's ID must be given.")
            print_pager(utils.get_single_quote(id).prettify())
        else:
            print("*** Unknown debug command.")
    
    # Meta
    
    def do_help(self, arg):
        """List available commands."""
        if arg in self.aliases:
            arg = self.aliases[arg].__name__[3:]
        cmd.Cmd.do_help(self, arg)
    
    def emptyline(self):
        return
    
    def pre_cmd(self, line):
        if line == "EOF":
            return self.do_exit()
        return line
    
    def default(self, line):
        cmd, arg, line = self.parseline(line)
        if cmd in self.aliases:
            return self.aliases[cmd](arg)
        print("*** Unknown syntax: {}".format(line))
        return False
    
    def get_names(self):
        return [n for n in dir(self.__class__) if n not in self.hiden_methods]
    
    def do_EOF(self, line):
        print()
        return True
    
    def do_exit(self, *args):
        return True

def main():
    parser = argparse.ArgumentParser(
        prog="DTCEverywhere",
        description="A complete viewer for DansTonChat quotes"
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true",
        help="Interactive mode"
    )
    subparsers = parser.add_subparsers(help="Commands", dest="command")
    # Runs the command.
    args = parser.parse_args()
    if args.interactive:
        try:
            DTCEShell().cmdloop()
        except KeyboardInterrupt:
            exit(0)
    else:
        print("*** Error: Not implemented yet. Try 'dtceverywhere -i'.")
        exit(0)

if __name__ == "__main__":
    main()

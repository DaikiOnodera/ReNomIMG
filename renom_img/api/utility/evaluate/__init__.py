import numpy as np
from .detection import get_prec_and_rec, get_ap_and_map, get_mean_iou
from .classification import precision_score, recall_score, f1_score, accuracy_score
from .segmentation import segmentation_iou, segmentation_precision, segmentation_recall, segmentation_f1, get_segmentation_metrics
from collections import defaultdict


class EvaluatorBase(object):

    def __init__(self, prediction, target):
        self.prediction = prediction
        self.target = target

    def build_report(self, class_names, headers, rows, last_line_heading, row_fmt, last_row=None, round_off=3):
        name_width = max(len(str(cn)) for cn in class_names)
        width = max(name_width, len(last_line_heading), round_off * 2)

        head_fmt = '{:>{width}s} ' + ' {:>12}' * (len(headers) - 1) + '{:>16}'
        report = head_fmt.format('', *headers, width=width)
        report += ' \n\n'

        for row in rows:
            report += row_fmt.format(*row, width=width, round_off=round_off)
        report += '\n'
        report += row_fmt.format(last_line_heading,
                                 *last_row,
                                 width=width, round_off=round_off)
        return report

    def plot_graph(self, x, y, title=None, x_label=None, y_label=None):
        import matplotlib.pyplot as plt

        plt.figure()
        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.plot(x, y)
        plt.show()


class EvaluatorDetection(EvaluatorBase):
    """ Evaluator for object detection tasks

    Args:
        prediction (list): A list of prediction results. The format is as follows
        target (list): A list of ground truth boxes and classes.
        num_class (int): The number of classes

    .. code-block :: python
        :caption: **Example of the arguments, "prediction" and "target".**

            [
                [ # Objects of 1st image.
                    {'box': [x(float), y, w, h], 'class': class_id(int), 'score': score},
                    {'box': [x(float), y, w, h], 'class': class_id(int), 'score': score},
                    ...
                ],
                [ # Objects of 2nd image.
                    {'box': [x(float), y, w, h], 'class': class_id(int), 'score': score},
                    {'box': [x(float), y, w, h], 'clas': class_id(int), 'score': score},
                    ...
                ]
            ]

    Example:
            >>> evaluator = EvaluatorDetection(pred, gt)
            >>> evaluator.mAP()
            >>> evaluator.mean_iou()
    """

    def __init__(self, prediction, target, num_class=None):
        super(EvaluatorDetection, self).__init__(prediction, target)
        self.num_class = num_class

    def mAP(self, iou_thresh=0.5, round_off=3):
        """ Returns mAP (mean Average Precision)

        Args:
            iou_thresh(float): IoU threshold. The default value is 0.5.
            round_off(int): The number of output decimal

        Returns:
            (float): mAP(mean Average Precision).
        """

        prec, rec, _, _ = get_prec_and_rec(self.prediction, self.target, self.num_class, iou_thresh)
        _, mAP = get_ap_and_map(prec, rec, round_off)
        return mAP

    def AP(self, iou_thresh=0.5, round_off=3):
        """ Returns AP(Average Precision) for each class.

        :math:`AP = 1/11 \sum_{r \in \{0.0,..1.0\}} AP_{r}`

        Args:
            iou_thresh: IoU threshold. The default value is 0.5.
            round_off(int): The number of output decimal

        Returns:
            (dictionary): AP for each class. The format is as follows

        .. code-block :: python

            {
                class_id1(int): AP1 (float),
                class_id2(int): AP2 (float),
                class_id3(int): AP3 (float),
            }
        """

        prec, rec, _, _ = get_prec_and_rec(self.prediction, self.target, self.num_class, iou_thresh)
        AP, _ = get_ap_and_map(prec, rec, round_off)
        return AP

    def mean_iou(self, iou_thresh=0.5, round_off=3):
        """ Returns mean IoU for all classes

        Args:
            iou_thresh: IoU threshold. The default value is 0.5.
            round_off(int): The number of output decimal

        Returns:
            (float): Mean IoU
        """
        _, mean_iou = get_mean_iou(self.prediction, self.target,
                                   self.num_class, iou_thresh, round_off)
        return mean_iou

    def iou(self, iou_thresh=0.5, round_off=3):
        """ Returns IoU for each class

        Args:
            iou_thresh (float): IoU threshold. The default value is 0.5.
            round_off (int): The number of output decimal

        Returns:
            (dictionary): IoU for each class. The format is as follows

            .. code-block :: python

                {
                    class_id1(int): iou1 (float),
                    class_id2(int): iou2 (float),
                    class_id3(int): iou3 (float),
                }
        """

        iou, _ = get_mean_iou(self.prediction, self.target, self.num_class, iou_thresh, round_off)
        return iou

    def plot_pr_curve(self, iou_thresh=0.5, class_names=None):
        """ Plot a precision-recall curve.

        Args:
            iou_thresh(float): IoU threshold. The default value is 0.5.
            class_names(list): List of keys in a prediction list or string if you output precision-recall curve of only one class. This specifies which precision-recall curve of classes to output.
        """

        prec, rec, _, _ = get_prec_and_rec(self.prediction, self.target, self.num_class, iou_thresh)
        if not isinstance(class_names, list) and class_names is not None:
            class_names = [class_names]

        if class_names:
            for c in class_names:
                p = prec[c]
                r = rec[c]
                if r is None or len(r) == 0:
                    continue
                self.plot_graph(r, p, c, 'Recall', 'Precision')
        else:
            for c in list(prec.keys()):
                p = prec[c]
                r = rec[c]
                if r is None or len(r) == 0:
                    continue
                self.plot_graph(r, p, c, 'Recall', 'Precision')

    def prec_rec(self, iou_thresh=0.5):
        """ Return precision and recall for each class

        Args:
            iou_thresh(float): IoU threshold. Defaults to 0.5

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of precision for each class and a dictionary of recall for each class.\
                     The format is as follows.

        .. code-block :: python
            :caption: **Example of outputs.**

                ({
                    class_id1(int): [precision1(float), precision2(float), ..],
                    class_id2(int): [precision3(float), precision4(float), ..],
                },
                {
                    class_id1(int): [recall1(float), recall2(float), ..]
                    class_id2(int): [recall3(float), recall4(float), ..]
                })
        """

        precision, recall, _, _ = get_prec_and_rec(
            self.prediction, self.target, self.num_class, iou_thresh)
        return precision. recall

    def report(self, iou_thresh=0.5, round_off=3):
        """ Outputs a table which shows AP, IoU, the number of predicted instances for each class, and the number of ground truth instances for each class.

        Args:
            iou_thresh (flaot): IoU threshold. The default value is 0.5.
            round_off (int): The number of output decimal

        Returns:
            +--------------+----------+------------+-----------------+
            |              |    AP    |    IoU     |  #pred/#target  |
            +--------------+----------+------------+-----------------+
            | class_name1: |  0.091   |   0.561    |      1/13       |
            +--------------+----------+------------+-----------------+
            | class_name2: |  0.369   |   0.824    |      6/15       |
            +--------------+----------+------------+-----------------+
            |    \.\.\.\.  |          |            |                 |
            +--------------+----------+------------+-----------------+
            |mAP / mean IoU|  0.317   |   0.698    |     266/686     |
            +--------------+----------+------------+-----------------+

        """

        prec, rec, n_pred, n_pos_list = get_prec_and_rec(
            self.prediction, self.target, self.num_class, iou_thresh)
        AP, mAP = get_ap_and_map(prec, rec, round_off)
        iou = self.iou()
        class_names = list(AP.keys())
        mean_iou = self.mean_iou()

        headers = ["AP", "IoU", "  #pred/#target"]
        rows = []
        for c in class_names:
            rows.append((str(c), AP[c], iou[c], n_pred[c], n_pos_list[c]))
        last_line_heading = 'mAP / mean IoU'
        last_row = (mAP, mean_iou, np.sum(list(n_pred.values())), np.sum(list(n_pos_list.values())))
        row_fmt = '{:>{width}s} ' + ' {:>12.{round_off}f}' * \
            (len(headers) - 1) + ' {:>12d}/{:d}' + ' \n'

        return self.build_report(class_names, headers, rows, last_line_heading, row_fmt, last_row, round_off)


class EvaluatorClassification(EvaluatorBase):
    """ Evaluator for classification tasks

    Args:
        prediction (list): A list of predicted class
        target (list): A list of target class. The format is as follows

    .. code-block :: python
        :caption: **Example of the arguments, "prediction" and "target".**

            [
                class_id1(int),
                class_id2(int),
                class_id3(int),
            ]

    Example:
            >>> evaluator = EvaluatorClassification(prediction, target)
            >>> evaluator.precision()
            >>> evaluator.recall()
    """

    def __init__(self, prediction, target):
        super(EvaluatorClassification, self).__init__(prediction, target)

    def precision(self):
        """ Returns precision for each class and mean precision

        Returns:
            (tuple): 2 values are returned. Each element represents a dictioanry of precision for each class and the mean precision(float).\
                     The format is as follows.

        .. code-block :: python
            :caption: **Example of outputs.**

                ({
                    class_id1(int): precision(float),
                    class_id2(int): precision(float),
                }, mean_precision(float))
        """
        precision, mean_precision = precision_score(self.prediction, self.target)
        return precision, mean_precision

    def recall(self):
        """ Returns recall for each class and mean recall

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of recall for each class and the mean recall(float).\
                     The format is as follows.

        .. code-block :: python
            :caption: **Example of outputs.**

                ){
                    class_id1(int): recall(float),
                    class_id2(int): recall(float),
                }, mean_recall(float))
        """

        recall, mean_recall = recall_score(self.prediction, self.target)
        return recall, mean_recall

    def accuracy(self):
        """ Returns accuracy.

        Returns:
            (float): Accuracy
        """

        accuracy = accuracy_score(self.prediction, self.target)
        return accuracy

    def f1(self):
        """
        Returns f1 for each class and mean f1 score.

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of F1 score for each class and mean F1 score(float).\
                     The format is as follows.

        .. code-block :: python
            :caption: **Example of outputs.**

                ({
                    class_id1(int): f1 score(float),
                    class_id2(int): f1_score(float)
                }, mean_f1_score(float))
        """

        f1, mean_f1 = f1_score(self.prediction, self.target)
        return f1, mean_f1

    def report(self, round_off=3):
        """ Outputs a table which shows precision, recall, F1 score, the number of true positive pixels and the number of ground truth pixels for each class.

        Args:
            round_off(int): The number of output decimal

        Returns:
            +--------------+-------------+-------------+-------------+-----------------+
            |              |  Precision  |    recall   |   F1 score  |  #pred/#target  |
            +--------------+-------------+-------------+-------------+-----------------+
            | class_id1:   |    0.800    |    0.308    |    0.444    |      4/13       |
            +--------------+-------------+-------------+-------------+-----------------+
            | class_id2:   |    0.949    |    0.909    |    0.929    |    150/165      |
            +--------------+-------------+-------------+-------------+-----------------+
            |    \.\.\.\.  |             |             |             |                 |
            +--------------+-------------+-------------+-------------+-----------------+
            |   Average    |    0.364    |    0.500    |    0.421    |    742/1256     |
            +--------------+-------------+-------------+-------------+-----------------+

        """
        precision, mean_precision = self.precision()
        recall, mean_recall = self.recall()
        f1, mean_f1 = self.f1()
        accuracy = self.accuracy()
        class_names = list(precision.keys())

        tp = defaultdict(int)
        true_sum = defaultdict(int)

        for p, t in zip(self.prediction, self.target):
            true_sum[t] += 1
            if p == t:
                tp[p] += 1

        headers = ["Precision", "Recall", "F1 score", "#pred/#target"]
        rows = []
        for c in class_names:
            rows.append((str(c), precision[c], recall[c], f1[c], tp[c], true_sum[c]))
        last_line_heading = 'Average'
        last_row = (mean_precision, mean_recall, mean_f1, np.sum(
            list(tp.values())), np.sum(list(true_sum.values())))
        row_fmt = '{:>{width}s} ' + ' {:>12.{round_off}f}' * \
            (len(headers) - 1) + ' {:>12d}/{:d}' + ' \n'

        report = self.build_report(class_names, headers, rows,
                                   last_line_heading, row_fmt, last_row, round_off)
        report += '\n'
        report += ('Accuracy' + ' {:>12.{round_off}f}'.format(accuracy, round_off=round_off))
        return report


class EvaluatorSegmentation(EvaluatorBase):
    """ Evaluator for classification tasks

    Args:
        prediction (list): A list of predicted class
        target (list): A list of target class. The format is as follows
        ignore_class(int): background class is ignored in the output table. defaults to 0.

    .. code-block :: python
        :caption: **Example of the arguments, "prediction" and "target".**

            [
                class_id1(int),
                class_id2(int),
                class_id3(int),
            ]

    Example:
            >>> evaluator = EvaluatorSegmentation(prediction, target)
            >>> evaluator.iou()
            >>> evaluator.precision()
    """

    def __init__(self, prediction, target, ignore_class=0):
        super(EvaluatorSegmentation, self).__init__(prediction, target)
        self.ignore_class = [ignore_class] if isinstance(ignore_class, int) else ignore_class

    def iou(self, round_off=3):
        """ Returns iou for each class

        Args:
            round_off(int): The number of output decimal

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of IoU for each class and mean IoU (float).
        """

        iou, mean_iou = segmentation_iou(self.prediction,
                                         self.target,
                                         round_off=round_off,
                                         ignore_class=self.ignore_class)
        return iou, mean_iou

    def precision(self, round_off=3):
        """ Returns precision for each class

        Args:
            round_off(int): The number of output decimal

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of precision for each class and the mean precision(float).
        """

        precision, mean_precision = segmentation_precision(self.prediction,
                                                           self.target,
                                                           round_off=round_off,
                                                           ignore_class=self.ignore_class)
        return precision, mean_precision

    def recall(self, round_off=3):
        """ Returns recall for each class and mean recall

        Args:
            round_off(int): The number of output decimal

        Returns:
            (tuple): 2 values are returned. Each element represents a dicitonary of recall for each class and mean recall(float).
        """

        recall, mean_recall = segmentation_recall(self.prediction,
                                                  self.target,
                                                  round_off=round_off,
                                                  ignore_class=self.ignore_class)
        return recall, mean_recall

    def f1(self, round_off=3):
        """ Returns f1 for each class and mean f1 score

        Args:
            round_off(int): The number of output decimal

        Returns:
            (tuple): 2 values are returned. Each element represents a dictionary of F1 score for each class and mean F1 score(float).
        """

        f1, mean_f1 = segmentation_f1(self.prediction,
                                      self.target,
                                      round_off=round_off,
                                      ignore_class=self.ignore_class)
        return f1, mean_f1

    def report(self, round_off=3):
        """ Outputs a table which shows IoU, precision, recall, F1 score, the number of true positive pixels and the number of ground truth pixels for each class.

        Args:
            round_off(int): The number of output decimal

        Returns:
            +--------------+----------+------------+-------------+-------------+-----------------+
            |              |    IoU   |  Precision |    recall   |   F1 score  |  #pred/#target  |
            +--------------+----------+------------+-------------+-------------+-----------------+
            | class_id1:   |  0.178   |   0.226    |    0.457    |    0.303    |  26094/571520   |
            +--------------+----------+------------+-------------+-------------+-----------------+
            | class_id2:   |  0.058   |   0.106    |    0.114    |    0.110    |  25590/224398   |
            +--------------+----------+------------+-------------+-------------+-----------------+
            |    \.\.\.\.  |          |            |             |             |                 |
            +--------------+----------+------------+-------------+-------------+-----------------+
            |   Average    |  0.317   |   0.698    |    0.404    |    0.259    | 5553608/18351769|
            +--------------+----------+------------+-------------+-------------+-----------------+

        """
        precision, mean_precision, \
            recall, mean_recall, \
            f1, mean_f1, iou, \
            mean_iou, tp, true_sum = get_segmentation_metrics(self.prediction,
                                                              self.target,
                                                              round_off=round_off,
                                                              ignore_class=self.ignore_class)

        headers = ["IoU", "Precision", "Recall", "F1 score", "#pred/#target"]
        rows = []
        class_names = list(precision.keys())

        for c in class_names:
            rows.append((str(c), iou[c], precision[c], recall[c], f1[c], tp[c], true_sum[c]))
        last_line_heading = 'Average'
        last_row = (mean_iou, mean_precision, mean_recall, mean_f1, np.sum(
            list(tp.values())), np.sum(list(true_sum.values())))
        row_fmt = '{:>{width}s} ' + ' {:>12.{round_off}f}' * \
            (len(headers) - 1) + ' {:>12d}/{:d}' + ' \n'

        report = self.build_report(class_names, headers, rows,
                                   last_line_heading, row_fmt, last_row, round_off)
        report += '\n'
        return report
